import numpy as np
import time
import sys
import pickle
from players import get_player_template, random_player
from core_loop import init_players, core_loop
from utils import lazy_pickle
from read_data import get_data
from itertools import product
from copy import deepcopy
from structure import init_problem, cleanup_solution


seed = 50
real_data = 50
D = 5
N = 50
T = 48
pt = 'pesimistic'
flat = True

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

p1 = players[0]


data = deepcopy(p1)

data['T'] = 240
data['price'] = data['allprices']
data['load'] = data['allload']

mo, c_, v_ = init_problem(data)
mo.solve()

sol = cleanup_solution(mo, c_, v_, data)

load = data['load']
cost = 0
for l in range(240):
    if load[l] > 0:
        cost += data['price'][l, 3] * load[l]
    else:
        cost += data['price'][l, 0] * load[l]
print(cost)

for t in range(240 - 48):


    
l = 0

