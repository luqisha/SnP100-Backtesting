import pandas as pd
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt
import strategy.moving_average as ma

def RSI_signals(data, downThres =20 , upperThres =50, DiffRate =0.0024 , rsitype =1 , SMA=[], SMArate =0.01, window=14, downmult=0.5, upmult=1):
    rsi = RSI(df=data, window=window, matype=2).rsi_14
    SMA = ma.AMA(data.close)
    holding = False
    signals = [0 for x in data.close]
    for i in range(window, len(data['close'])-1):
        if rsitype == 1: # RAW RSI
            condition1 = True
            condition2 = True
        elif rsitype == 2: # RSI+ SMArate
            condition1 = data['close'][i] < ((1-SMArate)*SMA[i])
            condition2 = data['close'][i] > ((1+SMArate)*SMA[i])
        elif rsitype == 3:
            condition1 = True
            condition2 = True
            downThres = rsi[i-window:i].mean() - (downmult*rsi[i-window:i].std())
            upperThres = rsi[i-window:i].mean() + (upmult*rsi[i-window:i].std())
        # Oversold - BUY
        if rsi[i]< downThres and condition1:
            downrate = (data['close'][i-1] - data ['close'][i])/ data['close'][i-1]
            if downrate <= DiffRate and downrate >=0:
                signals[i] = 1
        # Overbought - SELL
        elif rsi[i]> upperThres and condition2:
            uprate = (data['close'][i] - data['close'][i-1])/ data['close'][i-1]
            if uprate <= DiffRate:
                signals[i] = -1
    return signals


def RSI(df, window, matype=1):
    rsi_period = window

    # to calculate RSI, we first need to calculate the exponential weighted aveage gain and loss during the period
    df['gain'] = (df['close'] - df['open']).apply(lambda x: x if x > 0 else 0)
    df['loss'] = (df['close'] - df['open']).apply(lambda x: -x if x < 0 else 0)

    # here we use the same formula to calculate Exponential Moving Average
    if matype==2:
        df['ema_gain'] = df['gain'].ewm(span=rsi_period, min_periods=rsi_period).mean()
        df['ema_loss'] = df['loss'].ewm(span=rsi_period, min_periods=rsi_period).mean()
    if matype==1:
        df['ema_gain'] = df['gain'].rolling(rsi_period).mean()
        df['ema_loss'] = df['loss'].rolling(rsi_period).mean()

    # the Relative Strength is the ratio between the exponential avg gain divided by the exponential avg loss
    df['rs'] = df['ema_gain'] / df['ema_loss']

    # the RSI is calculated based on the Relative Strength using the following formula
    df['rsi_14'] = 100 - (100 / (df['rs'] + 1))
    return df

def show_rsi(df, lag):
    rsi = RSI(df, 14, 1).rsi_14
    std_rsi = pd.Series(((rsi-rsi.mean())/rsi.std()).values, index=rsi.index+pd.Timedelta(lag))
    plt.figure(figsize=(16,8))
    plt.plot(std_rsi, label="rsi normalized")
    plt.plot((df.close-df.close.mean())/df.close.std(), label="Price normalized")
    plt.legend()
