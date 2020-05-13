from itertools import product


N = 50
T = 48
D = 10
SEEDS = (1234, 2210, 1312, 6699)
DAYS = (20, 120, 200, -1)
SD = list(zip(SEEDS, DAYS))
TYPES = ['optimistic', 'pesimistic', 'neutral', 'solar', 'unique']
FREQ = [1, 5, None]
UPDATE_PRICES = [True, False]
FLAT_RATE = [True, False]
MARKET = [True, False]

iterator = product(SD, TYPES, FREQ, UPDATE_PRICES, FLAT_RATE, MARKET)

for (seed, day), pt, fq, up, ftou, market in iterator:
    no_market = fq is None
    no_market &= market is False
    no_market &= (pt in ['pesimistic', 'solar'])
    no_market &= up is False
    if (fq is None or market is False) and (not no_market):
        continue
    args = (N, T, D, pt, market, fq, seed, up, ftou, day)
    st = ",".join(map(str,args))
    print(st)

