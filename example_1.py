import numpy as np
import time
import pickle
from players import get_player_template, random_player
from core_loop import init_players, core_loop
from utils import lazy_pickle


PREF = "res/"


def run(N, T, D, pt, market, freq, seed, onlyprice=False):

    r = np.random.RandomState(seed)

    players = dict( (n, random_player(T, D, pt, r)) for n in range(N))

    for p in range(N):
        players[p]['freq'] = freq

    CONFIG = {
            'ROUNDS': T * (D - 1) + 1,
            'SLICE': T,
            'RANDOM_STATE': r,
            'MARKET': market,
            'ONLYPRICE': onlyprice,
            }

    start = time.perf_counter()
    core_loop(players, CONFIG)
    end = time.perf_counter() - start

    for k, pl in players.items():
        pl.pop('model', None)
        pl.pop('con', None)
        pl.pop('var', None)

    return (end, players)


N = 50
T = 48
D = 10
for seed in [1234, 69, 1312, 2210]:
    args = (N, T, D, 'pesimistic', False, None, seed)
    s = PREF + "-".join(map(str,args))
    lazy_pickle(s)(run)(*args)

TYPES = ['optimistic', 'pesimistic', 'neutral', 'solar', 'unique']
for tp in TYPES:
    for fq in [1, 5]:
        for seed in [1234, 69, 1312, 2210]:

            args = (N, T, D, tp, True, fq, seed)
            s = PREF + "-".join(map(str,args))
            lazy_pickle(s)(run)(*args)


TYPES = ['optimistic', 'pesimistic', 'neutral', 'solar', 'unique']
for tp in TYPES:
    for fq in [1, 5]:
        for seed in [1234, 69, 1312, 2210]:

            args = (N, T, D, tp, True, fq, seed, True)
            s = PREF + "-".join(map(str,args))
            lazy_pickle(s)(run)(*args)
