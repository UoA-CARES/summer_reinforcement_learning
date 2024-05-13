import torch
from torch import nn

from cares_reinforcement_learning.networks.encoders.autoencoder import Encoder
from cares_reinforcement_learning.util.common import SquashedNormal


class Actor(nn.Module):
    # DiagGaussianActor
    """torch.distributions implementation of an diagonal Gaussian policy."""

    def __init__(self, encoder: Encoder, num_actions: int):
        super().__init__()

        self.encoder = encoder

        self.hidden_size = [1024, 1024]
        self.log_std_bounds = [-10, 2]

        self.act_net = nn.Sequential(
            nn.Linear(self.encoder.latent_dim, self.hidden_size[0]),
            nn.ReLU(),
            nn.Linear(self.hidden_size[0], self.hidden_size[1]),
            nn.ReLU(),
        )

        self.mean_linear = nn.Linear(self.hidden_size[1], num_actions)
        self.log_std_linear = nn.Linear(self.hidden_size[1], num_actions)

    def forward(
        self, state: torch.Tensor, detach_encoder: bool = False
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:

        state_latent = self.encoder(state, detach=detach_encoder)

        x = self.act_net(state_latent)
        mu = self.mean_linear(x)
        log_std = self.log_std_linear(x)

        # Bound the action to finite interval.
        # Apply an invertible squashing function: tanh
        # employ the change of variables formula to compute the likelihoods of the bounded actions

        # constrain log_std inside [log_std_min, log_std_max]
        log_std = torch.tanh(log_std)

        log_std_min, log_std_max = self.log_std_bounds
        log_std = log_std_min + 0.5 * (log_std_max - log_std_min) * (log_std + 1)

        std = log_std.exp()

        dist = SquashedNormal(mu, std)
        sample = dist.rsample()
        log_pi = dist.log_prob(sample).sum(-1, keepdim=True)

        return sample, log_pi, dist.mean
