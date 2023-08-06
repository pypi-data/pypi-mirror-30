from examples.data import *
from collections import OrderedDict
from episodic_memory.world import *
from episodic_memory.utils import *
from episodic_memory.agent import *
import numpy as np
np.random.seed(0)

""" navie world """
naive_param_vecs = get_naive_param_vec_set()
# constants
param_vec_dim = len(naive_param_vecs[0])
max_realization_idx = 1
num_ongoing_vecs = 1
# event constants
num_events = 1
event_length = 50
# agent constants
min_matches = 1
max_mismatch = 0
buffer_size = 13

""""""
# defined the num branches
n_branches = 2
event_len = 8
n_params = 8
ohv_dim = n_params * n_branches

# train/test parameters
train_set_size = 10000
test_set_size = 500

X, Y, obs, pred = get_data(n_params, n_branches, event_len)
obs

# """set up the world to generate events """
# # set up world 0
# w0 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx,
#            [naive_param_vecs[0]])
# w0.initialize_situations(num_events)
# # set up world 1
# w1 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx,
#            [naive_param_vecs[1]])
# w1.initialize_situations(num_events)
# # print info
# # w0.print_info()
# # w1.print_info()
# # make events
# obs_seq0, pred_seq0 = w0.make_event_seq(event_length)
# obs_seq1, pred_seq1 = w1.make_event_seq(event_length)
# obs_seq2, pred_seq0 = w0.make_event_seq(event_length)
# print(obs_seq0)
# print(obs_seq1)
# print(obs_seq2)

# agent
agent = Agent(min_matches, max_mismatch, buffer_size)
agent

verbose = True
num_episodes_retrieved0 = agent.process_event(obs[:event_len], verbose)

agent.form_episode()
num_episodes_retrieved1 = agent.process_event(obs[:event_len], verbose)
np.shape(num_episodes_retrieved1)

num_episodes_retrieved = np.concatenate(
    [num_episodes_retrieved0,
     num_episodes_retrieved1]
)

"""
"""
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 4))
plt.stem(num_episodes_retrieved, label='"retrieval spikes"')
# plt.plot(num_episodes_retrieved)
# plt.axvline(event_length, color='black', linestyle='--')
# plt.axvline(event_length * 2, color='black', linestyle='--',
#             label='"event boundaries"')
plt.title('movie 1st half -> 1 day gap -> movie 2nd half')
plt.xlabel('time ticks')
plt.ylabel('num episodes retrieved ')
plt.legend()
