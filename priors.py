import numpy as np
from collections import deque

"""
This module deals with priors from players.
All data related to priors is stored in the main player dictionary.

Priors are assumed to be normal - normal (known deviation, unknown mu)

The relevant fields are as following:

Suffix used are: 
    qb (quantity buying),
    qs (quantity selling), 
    ps (price selling),
    pb (price buying),

key: `priors_{suffix}`
    Numpy array of shape (N, 3) where
    N is the number of different priors the player.
    
    First column represents player's mu
    Second column represents player's sigma
    Third column represents the known sigma

key `freq`. Integer: number of samples required before
    updating.

key `queue_{suffix}`
    List of deque (queues) where the samples
    are stored before they are processed. This is used
    together with the update frequency `freq`.

ket `slot2prior`
    List of integers of length equal to the number of slots
    in the simulation.
    Maps each time-slot with one of the priors.

key `price`
    Numpy array of size (Time-slots, 7)
    Each row stands for [price selling TEC, price sellig market, price buying market, price buying TEC, quant selling market, 0, quant buying market].

"""


def update_prior(mu, sigma, fixdev, obs):
    n = len(obs)
    avg = np.mean(obs)
    sigma_ = 1 / ((1 / sigma) + (n / fixdev))
    mu_ = ((mu / sigma) + (avg / fixdev)) * sigma_
    return mu_, sigma_

def convexify(arr):
    assert arr.shape[0] == 7
    ## Quantities
    if arr[4] > 0: arr[4] = 0
    if arr[6] < 0: arr[6] = 0
    ## Prices
    PS, PB = arr[0], arr[3]
    arr[:4] = np.clip(arr[:4], a_min=PS, a_max=PB)
    if arr[1] > arr[2]:
        m = np.mean(arr[1:3])
        arr[1:3] = [m, m]

def set_priors(start, end, data):

    ppb = data['priors_pb']
    pps = data['priors_ps']
    pqb = data['priors_qb']
    pqs = data['priors_qs']
    for i in range(start, end):
        index = data['slot2prior'][i] # Get right prior
        arr = data['price'][i - start]

        arr[1] = pps[index][0]
        arr[2] = ppb[index][0]
        arr[4] = pqs[index][0] * -1.0
        arr[6] = pqb[index][0]
        convexify(arr)

    return data

def set_prior_with_market(data, tq, tp):
    """
    Updates the cost function for the first
    time slot based on the results of the market.
    """


    if tq >= 0:
        set_, clear_, update_ = 6, 4, 2
    else:
        set_, clear_, update_ = 4, 6, 1
    
    data['price'][0, set_] = tq
    data['price'][0, clear_] = 0
    data['price'][0, update_] = tp
    convexify(data['price'][0])
    return data

def accumulate_sample(i, data, tq, tp):
    
    # TODO: add support to less priors than time-slots

    index = data['slot2prior'][i]
    qqb = data['queue_qb'][index]
    qqs = data['queue_qs'][index]
    qpb = data['queue_pb'][index]
    qps = data['queue_ps'][index]

    buying = data['history_pre_net'][i] > 0
    if np.allclose(tp, 0):
        if buying:
            qqb.append(0)
        else:
            qqs.append(0)
    elif tq > 0:
        qqb.append(tq)
        qpb.append(tp)
    else:
        qqs.append(-tq)
        qps.append(tp)


def update_current_prior(i, data, onlyprice):

    index = data['slot2prior'][i]
    freq = data.get('freq', 0)
    if freq is None:
        return
    
    if onlyprice:
        suffix = ['pb', 'ps']
    else:
        suffix = ['qb', 'qs', 'pb', 'ps']
    queues = [data['queue_{0}'.format(suf)][index] for suf in suffix]
    priors = [data['priors_{0}'.format(suf)][index] for suf in suffix]

    for p, q in zip(priors, queues):
        if len(q) >= freq:
            rem = [q.popleft() for _ in range(freq)]
            mu, sig = update_prior(p[0], p[1], p[2], rem)
            p[:2] = mu, sig

