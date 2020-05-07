import numpy as np
import time
import pickle
from players import get_player_template, random_player
from core_loop import init_players, core_loop
from utils import lazy_pickle


PREF = "res/"


def run(N, T, D, pt, market, freq, seed):

    r = np.random.RandomState(seed)

    players = dict( (n, random_player(T, D, pt, r)) for n in range(N))

    for p in range(N):
        players[p]['freq'] = freq

    CONFIG = {
            'ROUNDS': T * (D - 1) + 1,
            'SLICE': T,
            'RANDOM_STATE': r,
            'MARKET': market,
            }

    start = time.perf_counter()
    core_loop(players, CONFIG)
    end = time.perf_counter() - start

    for k, pl in players.items():
        pl.pop('model', None)
        pl.pop('con', None)
        pl.pop('var', None)

    return (end, players)

args = (50, 48, 10, 'optimistic', True, 1, 1234)
lazy_pickle(PREF + "50-48-10-opt-f1")(run)(*args)

args = (50, 48, 10, 'pesimistic', True, 1, 1234)
lazy_pickle(PREF + "50-48-10-pes-f1")(run)(*args)

args = (50, 48, 10, 'pesimistic', False, 1, 1234)
lazy_pickle(PREF + "50-48-10-pes-f1-nm")(run)(*args)

args = (50, 48, 10, 'neutral', True, 1, 1234)
lazy_pickle(PREF + "50-48-10-neut-f1")(run)(*args)

args = (50, 48, 10, 'solar', True, 1, 1234)
lazy_pickle(PREF + "50-48-10-sol-f1")(run)(*args)

args = (50, 48, 10, 'unique', True, 1, 1234)
lazy_pickle(PREF + "50-48-10-uni-f1")(run)(*args)


args = (50, 48, 10, 'optimistic', True, 2, 1234)
lazy_pickle(PREF + "50-48-10-opt-f2")(run)(*args)

args = (50, 48, 10, 'pesimistic', True, 2, 1234)
lazy_pickle(PREF + "50-48-10-pes-f2")(run)(*args)

args = (50, 48, 10, 'pesimistic', False, 2, 1234)
lazy_pickle(PREF + "50-48-10-pes-f2-nm")(run)(*args)

args = (50, 48, 10, 'neutral', True, 2, 1234)
lazy_pickle(PREF + "50-48-10-neut-f2")(run)(*args)

args = (50, 48, 10, 'solar', True, 2, 1234)
lazy_pickle(PREF + "50-48-10-sol-f2")(run)(*args)

args = (50, 48, 10, 'unique', True, 2, 1234)
lazy_pickle(PREF + "50-48-10-uni-f2")(run)(*args)


args = (50, 48, 10, 'optimistic', True, 5, 1234)
lazy_pickle(PREF + "50-48-10-opt-f5")(run)(*args)

args = (50, 48, 10, 'pesimistic', True, 5, 1234)
lazy_pickle(PREF + "50-48-10-pes-f5")(run)(*args)

args = (50, 48, 10, 'pesimistic', False, 5, 1234)
lazy_pickle(PREF + "50-48-10-pes-f5-nm")(run)(*args)

args = (50, 48, 10, 'neutral', True, 5, 1234)
lazy_pickle(PREF + "50-48-10-neut-f5")(run)(*args)

args = (50, 48, 10, 'solar', True, 5, 1234)
lazy_pickle(PREF + "50-48-10-sol-f5")(run)(*args)

args = (50, 48, 10, 'unique', True, 5, 1234)
lazy_pickle(PREF + "50-48-10-uni-f5")(run)(*args)
