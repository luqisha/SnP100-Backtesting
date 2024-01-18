import strategy.moving_average as ma
import pandas as pd

def keltner_signals(df, span, strategy=1, TimeperiodLong =40, TimeperiodShort =4, AdaWin =4):
    signal, mid, upper, lower, atr = keltner(df, span, strategy=strategy, TimeperiodLong =TimeperiodLong, TimeperiodShort =TimeperiodShort, AdaWin =AdaWin)
    return signal

def keltner_atr(df, span, strategy=1, TimeperiodLong =40, TimeperiodShort =4, AdaWin =4):
    signal, mid, upper, lower, atr = keltner(df, span, strategy=strategy, TimeperiodLong =TimeperiodLong, TimeperiodShort =TimeperiodShort, AdaWin =AdaWin)
    return atr

def keltner(df, span, strategy, TimeperiodLong, TimeperiodShort, AdaWin):
    tr=[0]
    for i in range(1, len(df.index)):
        tr.append(max(df["high"].iloc[i] - df["low"].iloc[i], df["high"].iloc[i] - df["close"].iloc[i-1], df["close"].iloc[i-1] - df["low"].iloc[i]))
    trange = pd.Series(tr, index=df.index)
    atr = trange.rolling(span).mean()
    mid = ma.AMA(df.close, TimeperiodLong = TimeperiodLong, TimeperiodShort = TimeperiodShort, AdaWin = AdaWin)
    upper = pd.Series(mid+(2*atr), index=df.index)
    lower = pd.Series(mid-(2*atr), index=df.index)
    signal = pd.Series([0 for x in mid], index=df.index)
    if strategy==1:
        for i in range(len(signal)):
            if df.close[i]<mid[i]:
                signal[i] = 1
            elif df.close[i]>upper[i]:
                signal[i] = -1
            else:
                signal[i] = 0
    elif strategy==2:
        for i in range(len(signal)):
            if all([close<mid for close,mid in zip(df.close.iloc[i-2:i+1], mid[i-1:i+1])]):
                signal[i] = -1
            elif all([close>upper for close,upper in zip(df.close.iloc[i-2:i+1], upper[i-1:i+1])]):
                signal[i] = 1
    elif strategy==3:
        for i in range(len(signal)):
            if df.close[i]<mid[i]:
                signal[i] = 1
            elif all([close<mid for close,mid in zip(df.close.iloc[i-2:i+1], mid[i-1:i+1])]):
                signal[i] = -1
            else:
                signal[i] = 0
        
    return pd.Series(signal, index=df.index), mid, upper, lower, atr

def show_keltner_orders(df, span, strategy):
    signals, mid, upper, lower = keltner(bxm, span, strategy)
    buys = [signals[i]*df.close[i] if signals[i]==1 else None for i in range(len(signals))]
    sells = [abs(signals[i])*df.close[i]  if signals[i]==-1 else None for i in range(len(signals))]
    df.index = pd.DatetimeIndex(df.timestamp)
    plt.figure(figsize=(15,10))
    plt.plot(df.index, df.close, label="CSIX", color="black")
    plt.plot(df.index, mid, label="mid", color="blue")
    plt.plot(df.index, upper, label="upper", color="green")
    plt.plot(df.index, buys, 'bo')
    plt.plot(df.index, sells, 'ro')
    # plt.plot(csix.index, lower, label="lower", color="red")
    plt.legend()
    display(plt.show())