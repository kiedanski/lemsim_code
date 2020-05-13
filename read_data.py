# import os
# import sys
# parentdir = os.path.abspath(__file__)
# parentdir = os.path.dirname(parentdir)
# parentdir = os.path.dirname(parentdir)
# sys.path.insert(0, parentdir)

import numpy as np
import pandas as pd
import time
import datetime

def get_data(start, duration, N, r):

    FILE_NAME = 'data/data.csv'
    df = pd.read_csv(FILE_NAME)
    df.index = pd.to_datetime(df.date)
    df = df.drop('date', axis=1)
    df = df.dropna(axis=1)

    TD = datetime.timedelta(days=1)
    STARTDATE = datetime.datetime(2012, 7, 1)

    st_ = STARTDATE + (TD * start)
    end_ = st_ + (TD * duration)

    data = df[st_ : end_][:-1]

    res = data.sample(n=N, axis=1, random_state=r).values.astype(float)
    return res
    





# def get_one_day_data(day, df):

    # nextday = datetime.timedelta(days=1) + day
    # mask_day = df['date'].between(str(day), str(nextday))
    # tmp = df[mask_day]
    # tmp = pd.pivot_table(tmp, index='date', columns='customer', values='power')
    # return tmp

# def get_data(init_date, randomstate, cant_users, filename, use_solar=True, sun_times=(15,30)):
 
    # df = pd.read_csv(filename)

    # date_ = datetime.date(*map(int, init_date.split('-')))
    # data = get_one_day_data(date_, df.copy()).values
    # NN = data.shape[0]
    # selected_users = randomstate.choice(range(NN), cant_users)
    # while True:
        # data_ = data[:, selected_users]
        # if use_solar:
            # solar = np.zeros_like(data_)
            # for t in range(sun_times[0], sun_times[1]):
                # solar[t, : cant_users // 2] = randomstate.uniform(-1, 0, cant_users // 2)
            # data_ += solar
            # yield data_
        # date_ = date_ + datetime.timedelta(days=1)
        # data = get_one_day_data(date_, df.copy()).values

# def read_prosumers(filename):

    # with open(filename) as fh: data = fh.readlines()

    # # Load prices
    # prices = {}
    # for line in data:
        # if line[0] == '>':
            # pieces = line.strip().split(',')
            # price = []
            # for p in pieces[1:]:
                # q, v = map(int, p.strip().split(';'))
                # print(q,v)
                # price.append(np.repeat(v, q))
            # price = np.hstack(price)
            # prices[pieces[0][1:].strip()] = price
    # print(prices)
# if __name__ == '__main__':
    # read_prosumers('data/sample_dataset.csv')
