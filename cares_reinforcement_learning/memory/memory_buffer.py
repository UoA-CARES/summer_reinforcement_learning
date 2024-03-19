import random
from collections import deque
import numpy as np


class MemoryBuffer:
    """
    A memory buffer to temporarily store transitions. It is like a transition
    pool. Only off-policy algorithms needs random sampling this buffer.

    """

    def __init__(self, max_capacity=int(1e6)):
        self.buffer = deque(maxlen=max_capacity)

    def __len__(self):
        return len(self.buffer)

    def add(self, *experience):
        """
        Add new transitions into the buffer. Be aware of the sequence. Should
        be consistent with how it is sampled.

        Example:

        memory.add(state, action, reward, next_state, done)

        :param experience: a tuple of a transition.
        """
        self.buffer.append(experience)

    def sample(self, batch_size):
        """
        Sample for training the agent.

        :param batch_size: It is pre-set by training configuration file.
        """
        batch_size = min(batch_size, len(self.buffer))
        experience_batch = random.sample(self.buffer, batch_size)
        transposed_batch = zip(*experience_batch)
        return transposed_batch

    def sample_consecutive(self, batch_size):
        """
        For training MBRL to predict rewards. The right next transition is
        sampled as well. WHEN THE BUFFER IS NOT SHUFFLED.

        (State, action, reward, next_state, next_action, next_reard)

        """
        max_length = len(self.buffer) - 1
        batch_size = min(batch_size, max_length)
        # A list of candidate indices includes all indices.
        candi_indices = list(range(max_length))
        sampled_indices = []  # randomly sampled indices that is okay.
        # In this way, the sampling time depends on the batch size rather than buffer size.
        first_sample = True  # Not check duplicate for first time sample.
        while True:
            # Sample size based on how many still needed.
            idxs = random.sample(candi_indices, batch_size - len(sampled_indices))
            for i in idxs:
                # Check if it is already sampled.
                already_sampled = False
                # Only check if it is not first time in the while loop.
                if not first_sample:
                    # compare with each item in the sampled.
                    for j in sampled_indices:
                        if j == i:
                            already_sampled = True
                if (self.buffer[i][4] is False) and (not already_sampled):
                    sampled_indices.append(i)
                if len(sampled_indices) == batch_size:
                    break
            first_sample = False
            if len(sampled_indices) == batch_size:
                break
        # Form the sampled data batch
        experience_batch = [
            self.buffer[i]
            + (
                self.buffer[i + 1][1],
                self.buffer[i + 1][2],
            )
            for i in sampled_indices
        ]
        transposed_batch = zip(*experience_batch)
        return transposed_batch

    def flush(self):
        """
        For on-policy PPO. Output all collected trajectories.
        And clear the buffer.

        :return:
        """
        experience = list(zip(*self.buffer))
        self.buffer.clear()
        return experience

    def clear(self):
        """
        Clear the buffer.
        """
        self.buffer.clear()
