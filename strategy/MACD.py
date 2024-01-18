import strategy.moving_average as ma
import pandas as pd


def macd_signals(df, short_period, long_period, signal_period):
    macd = df.close.ewm(span=short_period, min_periods=short_period).mean() - df.close.ewm(span=long_period, min_periods=long_period).mean()
    macd_sigs = macd.rolling(signal_period).mean()
    signal = pd.Series([0 for x in macd], index=df.index)
    for i in range(len(signal)):
        if macd[i]>macd_sigs[i] and macd[i]>0:
            signal[i] = 1
        elif macd[i]<macd_sigs[i] and macd[i]<0:
            signal[i] = -1
        else:
            signal[i] = 0
    return signal

def macd(df, short_period, long_period, signal_period):
    macd = df.close.ewm(span=short_period, min_periods=short_period).mean() - df.close.ewm(span=long_period, min_periods=long_period).mean()
    macd_sigs = macd.rolling(signal_period).mean()
    return macd, macd_sigs