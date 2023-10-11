"""
Example of using sub-parser, sub-commands and sub-sub-commands :-)
"""

import argparse

def environment_args(parent_parser):
    env_parser = argparse.ArgumentParser()
    env_parsers = env_parser.add_subparsers(title="Environment", description="OpenAI Gym or Deep Mind Control Suite", help='choose', dest='gym_environment', required=True)

    # create the parser for the DMCS sub-command
    parser_dmcs = env_parsers.add_parser('dmcs', help='Deep Mind Control Suite', parents=[parent_parser])
    required = parser_dmcs.add_argument_group('required arguments')
    required.add_argument('--domain', type=str, required=True)
    required.add_argument('--task', type=str, required=True)
    
    # create the parser for the OpenAI sub-command
    parser_openai = env_parsers.add_parser('openai', help='OpenAI Gymnasium', parents=[parent_parser])
    required = parser_openai.add_argument_group('required arguments')
    required.add_argument('--task', type=str, required=True)
    return env_parser

def algorithm_args(parent_parser):
    alg_parser = argparse.ArgumentParser(add_help=False)
    alg_parsers = alg_parser.add_subparsers(help='Select which RL algorith you want to use', dest='algorithm', required=True)

    # create the parser for TD3 with default parameters
    parser_TD3 = alg_parsers.add_parser('TD3', help='TD3', parents=[parent_parser])
    parser_TD3.add_argument('--actor_lr', type=float, default=1e-4)
    parser_TD3.add_argument('--critic_lr', type=float, default=1e-3)
    parser_TD3.add_argument('--gamma', type=float, default=0.99)
    parser_TD3.add_argument('--tau', type=float, default=0.005)
    
    # create the parser for DDPG with default parameters
    parser_DDPG = alg_parsers.add_parser('DDPG', help='DDPG', parents=[parent_parser])
    parser_DDPG.add_argument('--actor_lr', type=float, default=1e-4)
    parser_DDPG.add_argument('--critic_lr', type=float, default=1e-3)
    parser_DDPG.add_argument('--gamma', type=float, default=0.99)
    parser_DDPG.add_argument('--tau', type=float, default=0.005)

    # create the parser for SAC with default parameters
    parser_SAC = alg_parsers.add_parser('SAC', help='SAC', parents=[parent_parser])
    parser_SAC.add_argument('--actor_lr', type=float, default=1e-4)
    parser_SAC.add_argument('--critic_lr', type=float, default=1e-3)
    parser_SAC.add_argument('--gamma', type=float, default=0.99)
    parser_SAC.add_argument('--tau', type=float, default=0.005)

    # create the parser for PPO with default parameters
    parser_PPO = alg_parsers.add_parser('PPO', help='SAC', parents=[parent_parser])
    parser_PPO.add_argument('--actor_lr', type=float, default=1e-4)
    parser_PPO.add_argument('--critic_lr', type=float, default=1e-3)
    parser_PPO.add_argument('--gamma', type=float, default=0.99)
    parser_PPO.add_argument('--max_steps_per_batch', type=float, default=5000)

    # create the parser for DQN with default parameters
    parser_DQN = alg_parsers.add_parser('DQN', help='DQN', parents=[parent_parser])
    parser_DQN.add_argument('--lr', type=float, default=1e-3)
    parser_DQN.add_argument('--gamma', type=float, default=0.99)

    # create the parser for DuelingDQN with default parameters
    parser_DuelingDQN = alg_parsers.add_parser('DuelingDQN', help='DuelingDQN', parents=[parent_parser])
    parser_DuelingDQN.add_argument('--lr', type=float, default=1e-3)
    parser_DuelingDQN.add_argument('--gamma', type=float, default=0.99)

    # create the parser for DoubleDQN with default parameters
    parser_DoubleDQN = alg_parsers.add_parser('DoubleDQN', help='DoubleDQN', parents=[parent_parser])
    parser_DoubleDQN.add_argument('--lr', type=float, default=1e-3)
    parser_DoubleDQN.add_argument('--gamma', type=float, default=0.99)

    return alg_parser

def parse_args():
    parser = argparse.ArgumentParser(add_help=False)  # Add an argument
    
    # TODO 
    parser.add_argument('--memory', type=str, default="MemoryBuffer", help="Memory type - options: {MemoryBuffer, PER}")
    parser.add_argument('--image_observation', type=bool, default=False, help="Use image as the observation state from the environment")

    parser.add_argument('--G', type=int, default=10, help="Number of learning updates each step of training")
    parser.add_argument('--batch_size', type=int, default=32, help="Batch Size used during training")

    parser.add_argument('--max_steps_exploration', type=int, default=10000, help="Total number of steps for exploration before training")
    parser.add_argument('--max_steps_training', type=int, default=100000, help="Total number of steps to train the algorithm")

    parser.add_argument('--number_steps_per_evaluation', type=int, default=10000, help="The number of steps inbetween evaluation runs during training")
    parser.add_argument('--number_eval_episodes', type=int, default=10, help="The number of episodes to evaluate the agent on during training")

    parser.add_argument('--seed', type=int, default=571, help="The random seed to set for training")

    parser.add_argument('--plot_frequency', type=int, default=100, help="How many steps between updating the running plot of the training and evaluation data during training")
    parser.add_argument('--checkpoint_frequency', type=int, default=100, help="How many steps between saving check point models of the agent during training")

    parser = algorithm_args(parent_parser=parser)
    parser = environment_args(parent_parser=parser)
    
    return vars(parser.parse_args()) # converts to a dictionary
  
if __name__ == '__main__':
    print(parse_args())
