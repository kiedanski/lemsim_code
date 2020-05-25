import numpy as np
from collections import deque, defaultdict



def get_player_template(T, L, num_priors):

    data = {
        'T':                                              T,
        'L':                                              L,
        'num_slopes':                                     4,
        'efc':                                         0.95,
        'efd':                                         0.95,
        'bmax':                                        13.5,
        'bmin':                                           0,
        'charge':                                         0,
        'dmax':                                           1.25,
        'dmin':                                           1.25,
        'price':                            np.zeros((T,7)),
        'load':                               np.zeros((T)),
        'allprices':                       np.zeros((L, 7)),
        'allload':                              np.zeros(L),
        'allforecast':                          np.zeros(L),
        'priors_pb':              np.zeros((num_priors, 3)),
        'priors_ps':              np.zeros((num_priors, 3)),
        'priors_qb':              np.zeros((num_priors, 3)),
        'priors_qs':              np.zeros((num_priors, 3)),
        'queue_pb':    [deque() for _ in range(num_priors)],
        'queue_ps':    [deque() for _ in range(num_priors)],
        'queue_qb':    [deque() for _ in range(num_priors)],
        'queue_qs':    [deque() for _ in range(num_priors)],
        'freq':                                           1,
        'slot2prior':                           np.zeros(L),
    }
    return data

PRIOR_TYPES = {
        'pesimistic': lambda t, d: (
            t, np.tile(np.arange(t), d), 0),
        'optimistic': lambda t, d: (
            t, np.tile(np.arange(t), d), 0.3),
        'neutral': lambda t, d: (
            t, np.tile(np.arange(t), d), 0.1),
        'solar': lambda t, d: (
            2, np.tile([1 if np.abs(j - (t // 2)) < (t//4) else 0 for j in range(t)], d), 0),
        'unique': lambda t, d: (
            1, np.zeros(t * d).astype(int), 0.1),

}


def random_player(T, D, prior_type, r, flat=False, load=None, forcast=None, solar=True):

    L = T * D

    N_PRI, S2P, MARKUP = PRIOR_TYPES.get(prior_type)(T, D)
    
    PS = 10
    TR = 2 * (T // 3)
    if flat:
        PB = [30] * L
    else:
        PB = ([20] * TR + [30] * (T - TR)) * D

    template = get_player_template(T, L, N_PRI)

    if load is None:
        load = r.uniform(0, 4, L + T)
        if solar is True:
            for t in range(0, L + T, T):
                tmp = r.uniform(-0.3, 0, (3 * (T // 4) - (T // 4)))
                load[t + (T // 4): t + (3 * (T // 4))] += tmp
    if forcast is None:
        LO = load.reshape(-1, T)
        forecast = np.vstack([LO[:i, :].mean(axis=0) for i in range(1, D + 1)]).flatten()
        load = load[T:]

    template['allload'] = load
    template['allforcast'] = load
    template['allprices'][:, : 2] = PS
    template['allprices'][:, 2] = PB
    template['allprices'][:, 3] = PB

    template['slot2prior'] = S2P

    ### Priors Quantity

    template['priors_qb'][:, 0] = 10
    template['priors_qb'][:, 1] = 2
    template['priors_qb'][:, 2] = 1

    template['priors_qs'][:, 0] = 10
    template['priors_qs'][:, 1] = 2
    template['priors_qs'][:, 2] = 1

    ### Priors Price

    avg_price_buy = defaultdict(list)
    for i in range(L):
        avg_price_buy[S2P[i]].append(template['allprices'][i, 3])
    val_buy = np.array([np.mean(v) for k, v in avg_price_buy.items()])
    
    avg_price_sell = defaultdict(list)
    for i in range(L):
        avg_price_sell[S2P[i]].append(template['allprices'][i, 0])
    val_sell = np.array([np.mean(v) for k, v in avg_price_sell.items()])

    template['priors_pb'][:, 0] = val_buy * (1 - MARKUP)
    template['priors_pb'][:, 1] = template['priors_pb'][:, 0] * 0.2
    template['priors_pb'][:, 2] = template['priors_pb'][:, 0] * 0.1

    template['priors_ps'][:, 0] = val_sell * (1 + MARKUP)
    template['priors_ps'][:, 1] = template['priors_pb'][:, 0] * 0.2
    template['priors_ps'][:, 2] = template['priors_pb'][:, 0] * 0.1


    if prior_type == 'solar' and S2P.max() > 0:
        template['priors_pb'][1, 0] = val_buy[1] * 0.8
        template['priors_ps'][1, 0] = val_sell[0] * 1.2



    return template
