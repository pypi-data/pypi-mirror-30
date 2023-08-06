import numpy as np
from episodic_memory.memory import EpisodicMemory
from episodic_memory.buffer import Buffer
from copy import deepcopy


class Agent:
    """ An agent with an episodic memory system and a short-term memory system.
        It can process some event sequences and retrieve episode memory.
    """

    def __init__(self, min_matches, max_mismatch, buffer_size):
        # the consistency requirement during retrieval
        self.min_matches = min_matches
        # the tolerance parameter during retrieval
        self.max_mismatch = max_mismatch
        # the "short-term" memory buffer, a list of parameter values
        self.buffer = Buffer(size=buffer_size)
        # the "longer-term" memory buffer, a list of parameter value vector
        self.episodic_memory = EpisodicMemory(min_matches, max_mismatch)

    def reset_buffer(self):
        """ wipe out the buffer
        """
        buffer_size = self.buffer.size
        self.buffer = Buffer(size=buffer_size)

    def process_observation(self, observation, verbose=False):
        """ take observation and perform the corresponding updates
        """
        # TODO retrieve if uncertain
        # TODO should retrieve the best episode

        # update the buffer with the current observation
        self.buffer.load_vals(observation)
        log = '- Load observation: %s\n- Buffer: %s' % (
            observation, self.buffer.get_all_vals())
        # get all episode that satisfy all constraints
        candidates = self.episodic_memory.get_candidate_episodes(
            self.buffer.od, verbose)

        # retrieve the 1st episode
        num_episodes_retrieved = 0
        if len(candidates) > 0:
            self.buffer.load_vals(candidates[0])
            num_episodes_retrieved += 1
            log += '\n- Load episode: %s' % (candidates[0])
        if verbose:
            print(log)
        return num_episodes_retrieved

    def process_event(self, event, verbose=False):
        """ an event := a sequence of observations
        """
        event_length = len(event)
        num_episodes_retrieved = np.zeros((event_length,))
        for i in range(event_length):
            if verbose:
                print('Event: %d' % (i))
            num_episodes_retrieved[i] = self.process_observation(
                event[i], verbose)
        return num_episodes_retrieved

    def form_episode(self):
        """ take a snapshot of the stuff in the buffer
        """
        current_belief = self.buffer.get_all_vals()
        self.episodic_memory.add_episode(current_belief)

    def print_info(self):
        print('--- Agent2 INFO ---')
        self.buffer.print_info()
        self.episodic_memory.print_info()
        print()
