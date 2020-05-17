import numpy as np
import pandas as pd
import time
import datetime



    
def get_data(i, start, duration, df):

    df.index = pd.to_datetime(df.index)

    TD = datetime.timedelta(days=1)
    STARTDATE = datetime.datetime(2012, 8, 1)

    st_ = STARTDATE + (TD * start)
    end_ = st_ + (TD * duration)

    data = df[st_ : end_][:-1][str(i)].values.astype(float)

    return data
