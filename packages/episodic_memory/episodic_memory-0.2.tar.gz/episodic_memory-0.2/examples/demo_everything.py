import sys
sys.path.append('..')
from episodic_memory.world import *
from episodic_memory.utils import *
from episodic_memory.agent import *
import numpy as np
np.random.seed(0)

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')
sns.set(font_scale=1.2)

""" navie world """
naive_param_vecs = [[(i+1) for i in range(10)], [(i+11) for i in range(10)]]
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

# set up world 0
w0 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx,
           [naive_param_vecs[0]])
w0.initialize_situations(num_events)
# set up world 1
w1 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx,
           [naive_param_vecs[1]])
w1.initialize_situations(num_events)
# print info
w0
w1
# make events
obs_seq0, pred_seq0 = w0.make_event_seq(event_length)
obs_seq1, pred_seq1 = w1.make_event_seq(event_length)
obs_seq2, pred_seq0 = w0.make_event_seq(event_length)
print(obs_seq0)
print(obs_seq1)
print(obs_seq2)

# agent
agent = Agent(min_matches, max_mismatch, buffer_size)
agent
agent.episodic_memory.get_candidate_episodes(agent.buffer.od)


verbose = True
num_episodes_retrieved0 = agent.process_event(obs_seq0, verbose)
agent.form_episode()
num_episodes_retrieved1 = agent.process_event(obs_seq1, verbose)
num_episodes_retrieved2 = agent.process_event(obs_seq2, verbose)

num_episodes_retrieved = np.concatenate(
    [num_episodes_retrieved0,
     num_episodes_retrieved1,
     num_episodes_retrieved2]
)
print(num_episodes_retrieved1)
print(num_episodes_retrieved2)


""" plot """

plt.figure(figsize=(8, 4))
plt.stem(num_episodes_retrieved, label='"retrieval spikes"')
# plt.plot(num_episodes_retrieved)
plt.axvline(event_length, color='black', linestyle='--')
plt.axvline(event_length * 2, color='black', linestyle='--',
            label='"event boundaries"')
plt.title('movie 1st half -> 1 day gap -> movie 2nd half')
plt.xlabel('time ticks')
plt.ylabel('num episodes retrieved ')
plt.legend()
