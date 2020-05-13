from structure import init_problem, update_problem, cleanup_solution
from collections import deque
from priors import *
from market import MarketInterface, prepare_bid
import numpy as np


def init_players(players):
    P = len(players)
    L = players[0]['L']
    for i in range(P):
        data = players[i]
        mo, c_, v_ = init_problem(data)
        players[i]['model'] = mo
        players[i]['con'] = c_
        players[i]['var'] = v_
        players[i]['history_bat'] = np.zeros(L)
        players[i]['history_cost'] = np.zeros(L)
        players[i]['history_pre_net'] = np.zeros(L)
        players[i]['history_post_net'] = np.zeros(L)




def core_loop(players, config):

    ROUNDS = config['ROUNDS']
    SLICE = config['SLICE']
    r = config['RANDOM_STATE']
    P = len(players)
    MARKET = config.get('MARKET', True)
    ONLYPRICE = config.get('ONLYPRICE', False)

    init_players(players)
    welfare = np.zeros(ROUNDS)
    traded = np.zeros(ROUNDS)

    for i in range(ROUNDS):

        if MARKET: mar = MarketInterface(r)
        for p in range(P):

            data = players[p]
            mo, c_, v_ = data['model'], data['con'], data['var']
            data['price'] = data['allprices'][i: i + SLICE, :]
            data['load'] = data['allforecast'][i : i + SLICE]
            data['load'][0] = data['allload'][i]

            set_priors(i, i + SLICE, data)

            if MARKET:
                mo = update_problem(mo, c_, v_, data)
                _ = mo.solve()
                sol = cleanup_solution(mo, c_, v_, data)

                bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
                net = sol['net'][0]
                data['history_pre_net'][i] = net

                price = data['price'][0, :]
                bids = prepare_bid(p, net, price)
                if bids is not None:
                    for bi in bids:
                        id_bid = mar.accept_bid(bi)


        if MARKET:
            mar.clear()
        for p in range(P):

            data = players[p]
            data['commitment'] = None
            mo, c_, v_ = data['model'], data['con'], data['var']

            if MARKET:
                if p in mar.users_to_key:
                    mtq, mtp = mar.get_user_result(p)
                    set_prior_with_market(data, mtq, mtp)
                    accumulate_sample(i, data, mtq, mtp)

                    if not np.allclose(mtq, 0):
                        data['commitment'] = mtq

            
            mo = update_problem(mo, c_, v_, data)
            _ = mo.solve()
            sol = cleanup_solution(mo, c_, v_, data)

            bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
            net = sol['net'][0]
            data['history_bat'][i] = bat
            data['history_cost'][i] = sol['var'][0]
            data['history_post_net'][i] = sol['net'][0]

            data['charge'] += bat
            data['commitment'] = None
            update_current_prior(i, data, onlyprice=ONLYPRICE)

    return welfare, traded



