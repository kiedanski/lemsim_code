import numpy as np
import pandas as pd
import time
import sys
import pickle
from players import get_player_template, random_player
from core_loop import init_players, core_loop
from utils import lazy_pickle
from process_data import get_data
from itertools import product

DATA = 'data/home_data_2012-13.csv'
DATA_SOLAR = 'data/home_data_2012-13_rand_03.csv'
DATA_FORCAST = 'data/home_data_2012-13_forcast.csv'
DATA_SOLAR_FORCAST = 'data/home_data_2012-13_rand_03_forcast.csv'



def run(N, T, D, pt, market, freq, seed, onlyprice=False, flat=False, real_data=-1):


    r = np.random.RandomState(seed)
    player_ids = r.choice(np.arange(126), N, replace=False)

    data_original = pd.read_csv(DATA, index_col='date', parse_dates=True)
    data_forcast = pd.read_csv(DATA_FORCAST, index_col='date', parse_dates=True)
    dfs_nosolar = [data_original, data_forcast]

    data_solar= pd.read_csv(DATA_SOLAR, index_col='date', parse_dates=True)
    data_solar_forcast = pd.read_csv(DATA_SOLAR_FORCAST, index_col='date', parse_dates=True)
    dfs_solar = [data_solar, data_solar_forcast]

#    real_data = int(real_data)
#    if real_data > 0:
#        loads = get_data(real_data, D + 1, N, r)
#    else:
#        loads = None

    players = {}
    for n in range(N):
        has_solar = n <= (N // 2)
        DFS = dfs_solar if has_solar else dfs_nosolar
        if real_data > 0:
            load_ = get_data(n, real_data, D, DFS[0])
            forcast_ = get_data(n, real_data, D, DFS[1])
        else:
            load_ = None
            forcast_ = None
        val = random_player(T, D, pt, r, flat, load=load_, forcast=forcast_, solar=has_solar)
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

    s = PREF + "-".join(map(str,args)) + "?test6"
    start = time.perf_counter()
    lazy_pickle(s)(run)(*args)
    end = time.perf_counter()

    with open('times.txt', 'a') as fh:
        text = s + " {0:2f}\n".format(end - start)
        fh.write(text)

