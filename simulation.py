import numpy as np
import time
import sys
import pickle
from players import get_player_template, random_player
from core_loop import init_players, core_loop
from utils import lazy_pickle
from read_data import get_data
from itertools import product




def run(N, T, D, pt, market, freq, seed, onlyprice=False, flat=False, real_data=-1):


    r = np.random.RandomState(seed)

    real_data = int(real_data)
    if real_data > 0:
        loads = get_data(real_data, D + 1, N, r)
    else:
        loads = None


    players = {}
    for n in range(N):
        has_solar = n <= (N // 2)
        load_ = loads[:, n] if loads is not None else None
        val = random_player(T, D, pt, r, flat, load=load_, solar=has_solar)
        players[n] = val


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
    welfare, traded = core_loop(players, CONFIG)
    end = time.perf_counter() - start

    for k, pl in players.items():
        pl.pop('model', None)
        pl.pop('con', None)
        pl.pop('var', None)

    return (end, players, welfare, traded)

PREF = "res/second/"

if __name__ == "__main__":


    N, T, D, pt, market, fq, seed, up, ftou, day = sys.argv[1:]
    N = int(N)
    T = int(T)
    D = int(D)
    market = True if market == 'True' else False 
    seed = int(seed)
    up = True if up == 'True' else False
    ftou = True if ftou == 'True' else False 
    day = int(day)
    try:
        fq = int(fq)
    except ValueError:
        fq = None
    args = (N, T, D, pt, market, fq, seed, up, ftou, day)

    s = PREF + "-".join(map(str,args)) + "?test3"
    start = time.perf_counter()
    lazy_pickle(s)(run)(*args)
    end = time.perf_counter()

    with open('times.txt', 'a') as fh:
        text = s + " {0:2f}\n".format(end - start)
        fh.write(text)

