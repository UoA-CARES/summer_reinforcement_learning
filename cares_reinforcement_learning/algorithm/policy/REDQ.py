"""
Original Paper: https://arxiv.org/pdf/2101.05982.pdf
"""

import copy
import logging
import os
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

import cares_reinforcement_learning.util.helpers as hlp
from cares_reinforcement_learning.memory import MemoryBuffer
from cares_reinforcement_learning.networks.REDQ import Actor, Critic
from cares_reinforcement_learning.util.configurations import REDQConfig


class REDQ:
    def __init__(
        self,
        actor_network: Actor,
        ensemble_critic: Critic,
        config: REDQConfig,
        device: torch.device,
    ):
        self.type = "policy"
        self.gamma = config.gamma
        self.tau = config.tau

        self.learn_counter = 0
        self.policy_update_freq = config.policy_update_freq
        self.target_update_freq = config.target_update_freq

        self.device = device

        self.num_sample_critics = config.num_sample_critics

        # this may be called policy_net in other implementations
        self.actor_net = actor_network.to(device)
        self.actor_net_optimiser = torch.optim.Adam(
            self.actor_net.parameters(), lr=config.actor_lr
        )

        self.target_entropy = -self.actor_net.num_actions

        self.ensemble_size = config.ensemble_size

        self.ensemble_critic = ensemble_critic.to(self.device)
        self.target_ensemble_critic = copy.deepcopy(self.ensemble_critic).to(
            self.device
        )
        self.target_ensemble_critic.eval()  # never in training mode - helps with batch/drop out layers

        self.lr_ensemble_critic = config.critic_lr
        self.ensemble_critic_optimizers = [
            torch.optim.Adam(critic_net.parameters(), lr=self.lr_ensemble_critic)
            for critic_net in self.ensemble_critic.critics
        ]

        # Set to initial alpha to 1.0 according to other baselines.
        init_temperature = 1.0
        self.log_alpha = torch.tensor(np.log(init_temperature)).to(device)
        self.log_alpha.requires_grad = True
        self.log_alpha_optimizer = torch.optim.Adam([self.log_alpha], lr=1e-3)

    # pylint: disable-next=unused-argument
    def select_action_from_policy(
        self, state: np.ndarray, evaluation: bool = False, noise_scale: float = 0
    ) -> np.ndarray:
        # pylint: disable-next=unused-argument

        # note that when evaluating this algorithm we need to select mu as action
        # so _, _, action = self.actor_net.sample(state_tensor)
        self.actor_net.eval()
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).to(self.device)
            state_tensor = state_tensor.unsqueeze(0)
            if evaluation is False:
                (action, _, _) = self.actor_net(state_tensor)
            else:
                (_, _, action) = self.actor_net(state_tensor)
            action = action.cpu().data.numpy().flatten()
        self.actor_net.train()
        return action

    @property
    def alpha(self) -> torch.Tensor:
        return self.log_alpha.exp()

    def _update_critics(
        self,
        idx: np.ndarray,
        states: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        next_states: torch.Tensor,
        dones: torch.Tensor,
    ) -> list[float]:
        with torch.no_grad():
            with hlp.evaluating(self.actor_net):
                next_actions, next_log_pi, _ = self.actor_net(next_states)

            target_q_values_one = self.target_ensemble_critic.critics[idx[0]](
                next_states, next_actions
            )

            target_q_values_two = self.target_ensemble_critic.critics[idx[1]](
                next_states, next_actions
            )

            target_q_values = (
                torch.minimum(target_q_values_one, target_q_values_two)
                - self.alpha * next_log_pi
            )

            q_target = rewards + self.gamma * (1 - dones) * target_q_values

        critic_loss_totals = []

        for critic_net, critic_net_optimiser in zip(
            self.ensemble_critic.critics, self.ensemble_critic_optimizers
        ):
            q_values = critic_net(states, actions)

            critic_loss_total = 0.5 * F.mse_loss(q_values, q_target)

            critic_net_optimiser.zero_grad()
            critic_loss_total.backward()
            critic_net_optimiser.step()

            critic_loss_totals.append(critic_loss_total.item())

        return critic_loss_totals

    def _update_actor_alpha(
        self, idx: np.ndarray, states: torch.Tensor
    ) -> tuple[float, float]:
        pi, log_pi, _ = self.actor_net(states)

        qf1_pi = self.target_ensemble_critic.critics[idx[0]](states, pi)
        qf2_pi = self.target_ensemble_critic.critics[idx[1]](states, pi)

        min_qf_pi = torch.minimum(qf1_pi, qf2_pi)

        actor_loss = ((self.alpha * log_pi) - min_qf_pi).mean()

        self.actor_net_optimiser.zero_grad()
        actor_loss.backward()
        self.actor_net_optimiser.step()

        # update the temperature
        alpha_loss = -(self.log_alpha * (log_pi + self.target_entropy).detach()).mean()
        self.log_alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self.log_alpha_optimizer.step()

        return actor_loss.item(), alpha_loss.item()

    def train_policy(self, memory: MemoryBuffer, batch_size: int) -> dict[str, Any]:
        self.learn_counter += 1

        experiences = memory.sample_uniform(batch_size)
        states, actions, rewards, next_states, dones, _ = experiences

        batch_size = len(states)

        # Convert into tensor
        states_tensor = torch.FloatTensor(np.asarray(states)).to(self.device)
        actions_tensor = torch.FloatTensor(np.asarray(actions)).to(self.device)
        rewards_tensor = torch.FloatTensor(np.asarray(rewards)).to(self.device)
        next_states_tensor = torch.FloatTensor(np.asarray(next_states)).to(self.device)
        dones_tensor = torch.LongTensor(np.asarray(dones)).to(self.device)

        # Reshape to batch_size x whatever
        rewards_tensor = rewards_tensor.unsqueeze(0).reshape(batch_size, 1)
        dones_tensor = dones_tensor.unsqueeze(0).reshape(batch_size, 1)

        # replace=False so that not picking the same idx twice
        idx = np.random.choice(
            self.ensemble_size, self.num_sample_critics, replace=False
        )

        info: dict[str, Any] = {}

        # Update the Critics
        critic_loss_totals = self._update_critics(
            idx,
            states_tensor,
            actions_tensor,
            rewards_tensor,
            next_states_tensor,
            dones_tensor,
        )
        info["critic_loss_totals"] = critic_loss_totals

        if self.learn_counter % self.policy_update_freq == 0:
            # Update the Actor
            actor_loss, alpha_loss = self._update_actor_alpha(idx, states_tensor)
            info["actor_loss"] = actor_loss
            info["alpha_loss"] = alpha_loss
            info["alpha"] = self.alpha.item()

        if self.learn_counter % self.target_update_freq == 0:
            # Update ensemble of target critics
            for critic_net, target_critic_net in zip(
                self.ensemble_critic.critics, self.target_ensemble_critic.critics
            ):
                hlp.soft_update_params(critic_net, target_critic_net, self.tau)

        return info

    def save_models(self, filepath: str, filename: str) -> None:
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        torch.save(self.actor_net.state_dict(), f"{filepath}/{filename}_actor.pht")
        torch.save(
            self.ensemble_critic.state_dict(), f"{filepath}/{filename}_ensemble.pht"
        )
        logging.info("models has been saved...")

    def load_models(self, filepath: str, filename: str) -> None:
        actor_path = f"{filepath}/{filename}_actor.pht"
        ensemble_path = f"{filepath}/{filename}_ensemble.pht"

        self.actor_net.load_state_dict(torch.load(actor_path))
        self.ensemble_critic.load_state_dict(torch.load(ensemble_path))
        logging.info("models has been loaded...")
