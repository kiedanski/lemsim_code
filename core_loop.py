from structure import init_problem, update_problem, cleanup_solution
from collections import deque
from priors import *
import numpy as np


PERIOD = 32
SLICE = 8

all_data = np.random.uniform(-2, 2, PERIOD)
all_prices = np.zeros((PERIOD, 7))
all_prices[:, : 2] = 1
all_prices[:, 2] = np.repeat([2,3] * int(PERIOD / SLICE), [4, 4] * int(PERIOD / SLICE))
all_prices[:, 3] = all_prices[:, 2]

priors_pb = np.zeros((SLICE // 2, 3))
priors_pb[:, 0] = [1.99, 1.98, 2.99, 2.98] 
priors_pb[:, 1] = 1
priors_pb[:, 2] = 1

priors_ps = np.zeros((SLICE // 2, 3))
priors_ps[:, 0] = [1.01, 1.02, 1.03, 1.04] 
priors_ps[:, 1] = 1
priors_ps[:, 2] = 1

priors_qb = np.zeros((SLICE // 2, 3)) 
priors_qb[:, 0] = [10.1, 10.2, 10.3, 10.4] 
priors_qb[:, 1] = 2
priors_qb[:, 2] = 1

priors_qs = np.zeros((SLICE // 2, 3))
priors_qs[:, 0] = [11.01, 11.02, 11.03, 11.04] 
priors_qs[:, 1] = 2
priors_qs[:, 2] = 1

slot2prior = [0, 0, 1, 1, 2, 2, 3, 3] * (PERIOD // SLICE)

num_priors = priors_qs.shape[0]

data = {
    'T':          SLICE,
    'num_slopes': 4,
    'efc':        0.95,
    'efd':        0.95,
    'bmax':       13.5,
    'bmin':       0,
    'charge':     0,
    'dmax':       5,
    'dmin':       5,
    'price':    np.zeros((SLICE, 7)),
    'load':     np.zeros((SLICE)),
    'allprices': all_prices,
    'allload' : all_data,
    'priors_pb': priors_pb,    
    'priors_ps': priors_ps,    
    'priors_qb': priors_qb,    
    'priors_qs': priors_qs,    
    'queue_pb': [deque() for _ in range(num_priors)],
    'queue_ps': [deque() for _ in range(num_priors)],
    'queue_qb': [deque() for _ in range(num_priors)],
    'queue_qs': [deque() for _ in range(num_priors)],
    'freq': 2,
    'slot2prior': slot2prior,
}



mo, c_, v_ = init_problem(data)
nets = []
bats = []
for i in range(PERIOD - SLICE + 1):

    data['price'] = data['allprices'][i: i + SLICE, :]
    data['load'] = data['allload'][i : i + SLICE]
    set_priors(i, i + SLICE, data)
    print('PRE_MARKET', data['price'].round(3), sep='\n')
    mo = update_problem(mo, c_, v_, data)
    _ = mo.solve()
    sol = cleanup_solution(mo, c_, v_, data)
    
    bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
    net = sol['var'][0]

    nets.append(net)
    bats.append(bat)

    # if i == 0:
    mtq, mtp = 0.99, 1.7
    # else:
        # mtq, mtp = -0.5, 1.2
    set_prior_with_market(data, mtq, mtp) # TODO: possible fix if mtp > pb
    accumulate_sample(i, data, mtq, mtp)

    update_current_prior(i, data)



    print('POST MARKET', data['price'].round(3), sep='\n')
    
    if i == 2:
        break
    data['charge'] += bat



# GAP = PERIOD - SLICE + 1
# data['T'] = GAP
# data['charge'] = 0
# data['price'] = data['allprices'][: GAP, :]
# data['load'] = data['allload'][: GAP]
# mo, c_, v_ = init_problem(data)
# _ = mo.solve()
# sol2 = cleanup_solution(mo, c_, v_, data)

# print(sol2['obj'], sum(nets) -sum(bats))
