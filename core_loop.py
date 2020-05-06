from structure import init_problem, update_problem, cleanup_solution
from collections import deque
from priors import *
from market import MarketInterface
import numpy as np
import pymarket as pm

r = np.random.RandomState(seed=1234)

PERIOD = 32
SLICE = 8
P = 10
players = {}

for i in range(P):

    all_data = r.uniform(-3, 2, PERIOD)
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
    priors_qb[:, 0] = [0.1, 0.2, 0.3, 0.4] 
    priors_qb[:, 1] = 2
    priors_qb[:, 2] = 1

    priors_qs = np.zeros((SLICE // 2, 3))
    priors_qs[:, 0] = [.11, .21, .31, .41] 
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

    players[i] = data


for i in range(P):
    data = players[i]
    mo, c_, v_ = init_problem(data)
    players[i]['model'] = mo
    players[i]['con'] = c_
    players[i]['var'] = v_


def prepare_bid(id_, net_, price_):
    if np.allclose(net_, 0):
        return None
    else:
        buying = net_ > 0
    
    bids = []
    if buying:
        bid = (min(net_, price_[6]), price_[2], id_, True, 0)
        bids.append(bid)
        if net_ > price_[6]:
            bid = (net_ - price_[6], price_[3], id_, True, 0)
            bids.append(bid)
    else:
        bid = (-max(net_, price_[4]), price_[1], id_, False, 0)
        bids.append(bid)
        if net_ < price_[4]:
            bid = (-(net_ - price_[4]), price_[0], id_, False, 0)
            bids.append(bid)
    return bids




# nets = []
# bats = []
# for i in range(PERIOD - SLICE + 1):

mar = MarketInterface(r)


for i in range(1):
    print(i)
    for p in range(P):
        data = players[p]
        mo, c_, v_ = data['model'], data['con'], data['var']
        data['price'] = data['allprices'][i: i + SLICE, :]
        data['load'] = data['allload'][i : i + SLICE]
        set_priors(i, i + SLICE, data)
        # print('PRE_MARKET', data['price'].round(3), sep='\n')
        mo = update_problem(mo, c_, v_, data)
        _ = mo.solve()
        sol = cleanup_solution(mo, c_, v_, data)

        bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
        net = sol['var'][0]
        print(p, net)

        price = data['price'][0, :]
        bids = prepare_bid(p, net, price)
        if bids is not None:
            for bi in bids:
                id_bid = mar.accept_bid(bi)
                print(p, id_bid)


    mar.clear()
    for p in range(P):
        print(p)

        data = players[p]
        data['commitment'] = None
        mo, c_, v_ = data['model'], data['con'], data['var']

        if p in mar.users_to_key:
            mtq, mtp = mar.get_user_result(p)
            set_prior_with_market(data, mtq, mtp)
            accumulate_sample(i, data, mtq, mtp)

            if not np.allclose(mtq, 0):
                print(mtq)
                data['commitment'] = mtq

        
        mo = update_problem(mo, c_, v_, data)
        _ = mo.solve()
        sol = cleanup_solution(mo, c_, v_, data)

        bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
        net = sol['var'][0]

        data['charge'] += bat




    # if i == 0:
    # mtq, mtp = 0.99, 1.7
    # # else:
        # # mtq, mtp = -0.5, 1.2
    # set_prior_with_market(data, mtq, mtp) # TODO: possible fix if mtp > pb

    # update_current_prior(i, data)



    # print('POST MARKET', data['price'].round(3), sep='\n')
    
    # if i == 2:
        # break
    # data['charge'] += bat



# GAP = PERIOD - SLICE + 1
# data['T'] = GAP
# data['charge'] = 0
# data['price'] = data['allprices'][: GAP, :]
# data['load'] = data['allload'][: GAP]
# mo, c_, v_ = init_problem(data)
# _ = mo.solve()
# sol2 = cleanup_solution(mo, c_, v_, data)

# print(sol2['obj'], sum(nets) -sum(bats))
