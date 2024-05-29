import random

import numpy as np
from collections import deque


class LongMemoryBuffer:
  

    def __init__(self, max_capacity: int = int(1e3), **priority_params):
        self.priority_params = priority_params

        self.max_capacity = max_capacity
        self.memory_buffers = deque([], maxlen=self.max_capacity)
        self.min_reward = float('inf')
        self.replaced_episode_id = None
        self.replaced_episode_reward = -1
        self.min_index = -1

    def add(self, experience) -> None:
       
        episode_reward = experience[1]  # total_reward is at index 1
        
        if self.is_full():
            if episode_reward > self.min_reward:
                # Replace the experience with the minimum reward with the current one
                self.replaced_episode_id = self.memory_buffers[self.min_index][0]
                self.replaced_episode_reward = self.memory_buffers[self.min_index][1]
                self.memory_buffers[self.min_index] = experience
                # Update the minimum reward and index
                self.update_min_reward()
        else:
            # Add the new experience if the buffer is not full
            self.memory_buffers.append(experience)
            # Update the minimum reward and index
            #self.update_min_reward()
            self.min_reward = min(self.min_reward, episode_reward)

                
    
    def update_min_reward(self):
        if self.memory_buffers:
            min_entry = min(self.memory_buffers, key=lambda x: x[1])  # total_reward is at index 1
            self.min_reward = min_entry[1]
            self.min_index = self.memory_buffers.index(min_entry)
        else:
            self.min_reward = float('inf')
            self.min_index = -1
    
    def is_full(self):
        return len(self.memory_buffers) >= self.max_capacity
    
    def get_length(self):
        return len(self.memory_buffers)
    
    

    def sample_uniform(self, batch_size: int) -> tuple:
        #print(f"memory_buffers_len:{len(self.memory_buffers)}")
        # for experience in self.memory_buffers:
        #     print(f"episode_id:{experience[0]}, episode_reward:{experience[1]}")
        #     input()
       
       # Randomly sample experiences from buffer of size batch_size
        experience_batch = random.sample(self.memory_buffers, batch_size)
        #print(f"experience_batch:{experience_batch}")
        #input()
       
        episode_ids, episode_rewards = zip(*((experience[0], experience[1]) for experience in experience_batch))
        #print(f"episode_ids:{episode_ids}", f"episode_rewards:{episode_rewards}")
        #input()
        return episode_ids , episode_rewards
    
    
    def get_min_reward(self) -> float:
        """
        Returns the minimum reward in the long term memory buffer.

        Returns:
            float: The minimum reward in the buffer.
        """
        return self.min_reward
    
    def get_replaced_episode_id_reward(self) -> int:
        """
        Returns the episode id of the deleted episode in the long term memory buffer.

        Returns:
            int: The episode id of the deleted episode.
        """
        return self.replaced_episode_id, self.replaced_episode_reward
    
   