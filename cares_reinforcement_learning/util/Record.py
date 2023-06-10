import pandas as pd
from datetime import datetime
import os
import logging
import torch
import yaml
from cares_reinforcement_learning.util.Plot import plot_average
import math

# Python has no max int
MAX_INT = 9999999

class Record:
    
    def __init__(self, glob_log_dir=None, log_dir=None, networks={}, checkpoint_freq=None, config=None) -> None:
        
        self.glob_log_dir = glob_log_dir or 'rl_logs'
        self.log_dir = log_dir or datetime.now().strftime("%y_%m_%d_%H:%M:%S")
        self.dir = f'{self.glob_log_dir}/{self.log_dir}'
        
        self.data = pd.DataFrame() 
        self.checkpoint_freq = checkpoint_freq
        
        self.networks = networks    
        
        self.log_count = 0
        
        self.initial_log_keys = set()
        self.__initialise_directories()
        
        if config:
            with open(f'{self.dir}/config.yml', 'w') as outfile:
                yaml.dump(config, outfile, default_flow_style=False)
    
    def log(self, **logs):
        self.log_count += 1
        
        if not self.initial_log_keys:
            logging.info('Setting Log Values')
            self.initial_log_keys.union(logs.keys())
        
        if self.initial_log_keys != logs.keys():
            logging.warning('Introducing new columns')
            self.initial_log_keys = self.initial_log_keys.union(logs.keys())
        
        if self.checkpoint_freq and self.log_count % self.checkpoint_freq == 0:
            self.save(f'_checkpoint')
    
        self.data = pd.concat([self.data, pd.DataFrame([logs])], ignore_index=True)
        
        string = [f'{key}: {str(val):10s}' for key, val in logs.items()]
        string = ' | '.join(string)
        string = '| ' + string + ' |'

        print(string)
        
    def save(self, sfx='_final'):
        if self.data.empty:
            logging.warning('Trying to save an Empty Dataframe')
        
        self.data.to_csv(f'{self.dir}/data/data{sfx}.csv')
        
        for name, data in self.data.items():
            plot_average(
                x=range(len(data.dropna())), 
                y=data.dropna(), 
                x_label='x', 
                y_label=name, 
                title=f'Average {name}', 
                window_size=math.floor(len(data)/20), 
                file_path=f'{self.dir}/figures/{name}_avg{sfx}.png'
                )
        
        if self.networks:
            for name, network in self.networks.items():
                torch.save(network.state_dict(), f'{self.dir}/models/{name}{sfx}.pht')
        
    def __initialise_directories(self):
        if not os.path.exists(self.glob_log_dir):
            os.mkdir(self.glob_log_dir)
            
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        
        if not os.path.exists(f'{self.dir}/data'):
            os.mkdir(f'{self.dir}/data')
            
        if not os.path.exists(f'{self.dir}/models'):
            os.mkdir(f'{self.dir}/models')
            
        if not os.path.exists(f'{self.dir}/figures'):
            os.mkdir(f'{self.dir}/figures') 
