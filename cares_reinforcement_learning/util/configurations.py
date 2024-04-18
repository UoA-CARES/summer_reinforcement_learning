from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

# NOTE: If a parameter is a list then don't wrap with Optional leave as implicit optional - List[type] = default

file_path = Path(__file__).parent.resolve()


class SubscriptableClass(BaseModel):
    def __getitem__(self, item):
        return getattr(self, item)


class EnvironmentConfig(SubscriptableClass):
    task: str


class TrainingConfig(SubscriptableClass):
    seeds: List[int] = [10]

    plot_frequency: Optional[int] = 100
    checkpoint_frequency: Optional[int] = 100

    number_steps_per_evaluation: Optional[int] = 10000
    number_eval_episodes: Optional[int] = 10


class AlgorithmConfig(SubscriptableClass):
    """
    Configuration class for the algorithm.

    These attributes are common to all algorithms. They can be overridden by the specific algorithm configuration.

    Attributes:
        algorithm (str): Name of the algorithm to be used.
        G (Optional[int]): Updates per step UTD-raio, for the actor and critic.
        G_model (Optional[int]): Updates per step UTD-ratio for MBRL.
        buffer_size (Optional[int]): Size of the memory buffer.
        batch_size (Optional[int]): Size of the training batch.
        max_steps_exploration (Optional[int]): Maximum number of steps for exploration.
        max_steps_training (Optional[int]): Maximum number of steps for training.
        number_steps_per_train_policy (Optional[int]): Number of steps per updating the training policy.
    """

    algorithm: str = Field(description="Name of the algorithm to be used")
    G: Optional[int] = 1
    G_model: Optional[int] = 1
    buffer_size: Optional[int] = 1000000
    batch_size: Optional[int] = 256
    max_steps_exploration: Optional[int] = 1000
    max_steps_training: Optional[int] = 1000000
    number_steps_per_train_policy: Optional[int] = 1


class DQNConfig(AlgorithmConfig):
    algorithm: str = Field("DQN", Literal=True)
    lr: Optional[float] = 1e-3
    gamma: Optional[float] = 0.99

    exploration_min: Optional[float] = 1e-3
    exploration_decay: Optional[float] = 0.95


class DuelingDQNConfig(AlgorithmConfig):
    algorithm: str = Field("DuelingDQN", Literal=True)
    lr: Optional[float] = 1e-3
    gamma: Optional[float] = 0.99

    exploration_min: Optional[float] = 1e-3
    exploration_decay: Optional[float] = 0.95


class DoubleDQNConfig(AlgorithmConfig):
    algorithm: str = Field("DoubleDQN", Literal=True)
    lr: Optional[float] = 1e-3
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005

    exploration_min: Optional[float] = 1e-3
    exploration_decay: Optional[float] = 0.95


class PPOConfig(AlgorithmConfig):
    algorithm: str = Field("PPO", Literal=True)
    actor_lr: Optional[float] = 1e-4
    critic_lr: Optional[float] = 1e-3

    gamma: Optional[float] = 0.99
    max_steps_per_batch: Optional[int] = 5000


class DDPGConfig(AlgorithmConfig):
    algorithm: str = Field("DDPG", Literal=True)
    actor_lr: Optional[float] = 1e-4
    critic_lr: Optional[float] = 1e-3

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005


class TD3Config(AlgorithmConfig):
    algorithm: str = Field("TD3", Literal=True)
    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005


class SACConfig(AlgorithmConfig):
    algorithm: str = Field("SAC", Literal=True)
    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005


class DynaSACConfig(AlgorithmConfig):
    algorithm: str = Field("DynaSAC", Literal=True)
    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4

    alpha_lr: Optional[float] = 3e-4
    use_bounded_active: Optional[bool] = False
    num_models: Optional[int] = 5

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005

    horizon: Optional[int] = 3
    num_samples: Optional[int] = 10
    world_model_lr: Optional[float] = 0.001


class NaSATD3Config(AlgorithmConfig):
    algorithm: str = Field("NaSATD3", Literal=True)
    # actor_lr: Optional[float] = 1e-4
    # critic_lr: Optional[float] = 1e-3

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005

    latent_size: Optional[int] = 200
    intrinsic_on: Optional[int] = 1

    # lr_actor   = 1e-4
    # lr_critic  = 1e-3

    # lr_encoder = 1e-3
    # lr_decoder = 1e-3

    # lr_epm      = 1e-4
    # w_decay_epm = 1e-3


class CTD4Config(AlgorithmConfig):
    algorithm: str = Field("CTD4", Literal=True)

    actor_lr: Optional[float] = 1e-4
    critic_lr: Optional[float] = 1e-3
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    ensemble_size: Optional[int] = 3

    min_noise: Optional[float] = 0.0
    noise_decay: Optional[float] = 0.999999
    noise_scale: Optional[float] = 0.1

    fusion_method: Optional[str] = "kalman"  # kalman, minimum, average


class RDTD3Config(AlgorithmConfig):
    algorithm: str = Field("RDTD3", Literal=True)

    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    alpha: Optional[float] = 0.7

    noise_scale: Optional[float] = 0.1
    noise_decay: Optional[float] = 1


class PERTD3Config(AlgorithmConfig):
    algorithm: str = Field("PERTD3", Literal=True)

    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    alpha: Optional[float] = 0.6

    noise_scale: Optional[float] = 0.1
    noise_decay: Optional[float] = 1


class LAPTD3Config(AlgorithmConfig):
    algorithm: str = Field("LAPTD3", Literal=True)

    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    alpha: Optional[float] = 0.6
    min_priority: Optional[float] = 1.0

    noise_scale: Optional[float] = 0.1
    noise_decay: Optional[float] = 1


class PALTD3Config(AlgorithmConfig):
    algorithm: str = Field("PALTD3", Literal=True)

    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    alpha: Optional[float] = 0.4
    min_priority: Optional[float] = 1.0

    noise_scale: Optional[float] = 0.1
    noise_decay: Optional[float] = 1


class LA3PTD3Config(AlgorithmConfig):
    algorithm: str = Field("LA3PTD3", Literal=True)

    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    alpha: Optional[float] = 0.4
    min_priority: Optional[float] = 1.0
    prioritized_fraction: Optional[float] = 0.5

    noise_scale: Optional[float] = 0.1
    noise_decay: Optional[float] = 1


class MAPERTD3Config(AlgorithmConfig):
    algorithm: str = Field("MAPERTD3", Literal=True)

    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    alpha: Optional[float] = 0.7

    noise_scale: Optional[float] = 0.1
    noise_decay: Optional[float] = 1


class REDQConfig(AlgorithmConfig):
    algorithm: str = Field("REDQ", Literal=True)
    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    ensemble_size: Optional[int] = 10
    num_sample_critics: Optional[int] = 2

    G: Optional[int] = 20


class TQCConfig(AlgorithmConfig):
    algorithm: str = Field("TQC", Literal=True)
    actor_lr: Optional[float] = 3e-4
    critic_lr: Optional[float] = 3e-4
    alpha_lr: Optional[float] = 3e-4

    gamma: Optional[float] = 0.99
    tau: Optional[float] = 0.005
    top_quantiles_to_drop: Optional[int] = 2
    num_quantiles: Optional[int] = 25
    num_nets: Optional[int] = 5
