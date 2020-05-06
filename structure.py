import numpy as np
import scipy.sparse as sparse
import docplex.mp.model as cpx
from itertools import product
from numba import jit

def build_A(T, num_slopes, efc, efd, **kwargs):
    """
    Build the matrix A and the cost, no prices init.
    """
    I = np.eye(T)
    Z = np.zeros((T, T))

    OBJ = np.block(
        [[I, -I] for _ in range(num_slopes)]
    ) # Block matrix implementing the objective function

    LINK = np.hstack([-(1 / efc) * I, I * efd]) # linking z to other vars
    M = LINK.shape[1] + OBJ.shape[1]

    DI = np.tril(np.ones((T, T)))
    CONS = np.block([ # Constraint set
            [DI, -DI],
            [I, Z],
            [Z, I]
    ])
    c_m, c_n = CONS.shape

    Z_com = np.zeros(M)
    Z_com[0] = 1

    A = np.block([
        [OBJ, np.zeros((num_slopes * T, M - 2 * T))],
        [I, Z, LINK],
        [np.zeros((c_m, OBJ.shape[1])), CONS],
        [Z_com]
        ])

    cost = np.zeros(M)
    cost[T: 2 * T] = 1

    idx = [(t * T + i, i) for t in range(num_slopes) for i in range(T)]
    idx_x, idx_y = zip(*idx)

    A = sparse.csc_matrix(A)

    return A, cost, idx_x, idx_y

def build_lu(load, offset, charge, bmax, bmin, dmax, dmin, T, num_slopes, comm=None, **kwargs):

    M = T * (num_slopes + 4) + 1
    Z = np.zeros(T)
    O = np.ones(T)

    u = np.hstack([
        -offset, load, O * (bmax - charge),
        O * dmax, O * dmin, [np.inf]
        ])
    l = np.hstack([
        - np.ones(T * num_slopes) * np.inf, load,  O * (bmin - charge),
        Z, Z, [-np.inf]
        ])
    if comm is not None:
        if comm > 1:
            l[-1] = comm
        else:
            u[-1] = comm

    return u, l

@jit(nopython=True)
def build_price(prices, num_slopes):

    prices = prices.reshape(-1, 2 * num_slopes - 1)
    n, m = prices.shape
    res = np.zeros((n, num_slopes))
    for i in range(n):
        slopes = prices[i, :num_slopes]
        breakpoints = prices[i, num_slopes:]
        N = len(slopes)
        M = len(breakpoints)
        assert N == M + 1
        diff = np.diff(slopes)
        assert np.all(diff >= 0)
        assert np.all(np.diff(breakpoints) >= 0)

        offset = np.zeros(N)
        offset[1:] = - diff * breakpoints
        offset = np.cumsum(offset)

        pos = np.argmax(breakpoints >= 0)
        offset -= offset[pos]
        res[i] = offset

    return res


# def init_problem(data):
    # """
    # Initialize the OSQP Problem
    # """

    # prob = osqp.OSQP()
    # new_prices = data['price'][:, :data['num_slopes']].flatten('F') 

    # A_, cost_, idx_, idy_ = build_A(**data)
    # N, M = A_.shape
    # P_ = sparse.csc_matrix(np.zeros((M, M)))


    # offsets = build_price(data['price'], data['num_slopes']).flatten('F')
    # u_, l_ = build_lu(offset=offsets, **data)
    # A_[idx_, idy_] = new_prices

    # prob.setup(P=P_, q=cost_, A=A_, l=l_, u=u_, eps_abs=1e-8, eps_rel=1e-8,
            # linsys_solver='mkl pardiso', rho=1e-3)

    # controller = {
            # 'osqp': prob,
            # 'idx' : idx_,
            # 'idy' : idy_,
            # 'A': A_,
            # }

    # return controller

def init_problem(data, neginf=-1e5):

    model = cpx.Model(name="MIP Model")
    T = data['T']
    NS = data['num_slopes']
    EC, ED = (1 / data['efc']), data['efd']
    LOAD = data['load']

    prices = data['price'][:, : data['num_slopes']]
    offsets = build_price(data['price'], data['num_slopes'])

    t_vars = {
            j: model.continuous_var(
                lb=neginf,
                name="t_{0}".format(j))
            for j in range(T)
            }

    c_vars = {
            t: model.continuous_var(
                lb = 0,
                ub = data['dmax'],
                name="c_{0}".format(t))
            for t in range(T)
            }
    d_vars = {
            t: model.continuous_var(
                lb = 0,
                ub = data['dmin'],
                name="d_{0}".format(t))
            for t in range(T)
            }

    CUB = data['bmax'] - data['charge']
    CLB = data['bmin'] - data['charge']

    cons_charge_ub = {
            t: model.add_constraint(
                ct = model.sum(
                    c_vars[j] - d_vars[j] for j in range(t + 1)) <= CUB,
                ctname = "charge_ub_{0}".format(t)
                ) for t in range(T)
            }

    cons_charge_lb = {
            t: model.add_constraint(
                ct = model.sum(
                    c_vars[j] - d_vars[j] for j in range(t + 1)) >= CLB,
                ctname = "charge_lb_{0}".format(t)
                ) for t in range(T)
            }


    cons_cost = {
            (t, s): model.add_constraint(
                ct = prices[t][s] * model.sum(
                    EC * c_vars[t] - ED * d_vars[t]) - t_vars[t] <= - offsets[t][s] - prices[t][s] * LOAD[t],
                ctname = "cost_{0}_{1}".format(t, s)
                ) for t in range(T) for s in range(NS)
            }

    objective = model.sum(t_vars[j] for j in range(T))
    model.minimize(objective)

    CONS = [cons_charge_ub, cons_charge_lb, cons_cost]
    VARS = [t_vars, c_vars, d_vars]

    return model, CONS, VARS


def update_problem(model, CONS, VARS, data, EPS=1e-5):

    T, NS = data['T'], data['num_slopes']
    EC, ED = (1 / data['efc']), data['efd']
    LOAD = data['load']

    prices = data['price'][:, : data['num_slopes']]
    offsets = build_price(data['price'], data['num_slopes'])
    CUB = data['bmax'] - data['charge']
    CLB = data['bmin'] - data['charge']

    ec_prices = prices * EC
    ed_prices = - prices * ED

    rhs = - prices * LOAD.reshape(-1, 1) - offsets

    T_, C_, D_ = VARS

    cub = CONS[0]
    for t in range(T):
        cub[t].set_right_expr(CUB)

    clb = CONS[1]
    for t in range(T):
        clb[t].set_right_expr(CLB)

    cc = CONS[2]

    p = product(range(T), range(NS))
    for t, s in p:
        l = cc[(t, s)].get_expr_from_pos(0)

        new_vars = [(C_[t], ec_prices[t, s]),
                (D_[t], ed_prices[t,s])]
        l.set_coefficients(new_vars)
        cc[(t, s)].set_right_expr(rhs[t, s])

    c = model.find_matching_linear_constraints('commitment')
    if len(c) > 0:
        for c_iter in c:
            model.remove(c_iter)

    com = data.get('commitment', None)
    if com is not None:
        if com >= 0:
            model.add_constraint(
                    ct = model.sum( C_[0] * EC - D_[0] * ED + LOAD[0]) >= com - EPS,
                    ctname = 'commitment'
                    )
        else:
            model.add_constraint(
                    ct = model.sum(C_[0] * EC - D_[0] * ED + LOAD[0]) <= com + EPS,
                    ctname = 'commitment'
                    )


    return model

def cleanup_solution(model, con, var, data):

    obj = model.solution.objective_value
    T = len(var[0])
    var_res = np.zeros(3 * T)
    i = 0
    for v_ in var:
        for t in range(T):
            var_res[i] = v_[t].solution_value
            i += 1
    ec, ed = (1 / data['efc']), data['efd']
    net = ec * var_res[T: 2 * T] - var_res[2 * T:] * ed + data['load'] 

    res = {
            'obj': obj,
            'var': var_res,
            'net': net,
            }
    return res
