import numpy as np
import pandas as pd

def AMA_signals(df, long_window =30, short_window =2, ad_window =10, matype =1, strategy=1):
    ama = AMA(df.close, TimeperiodLong =long_window, TimeperiodShort =short_window, AdaWin =ad_window, matype =1)
    signals = pd.Series(0, index=df.index)
    for i in range(len(df.index)):
        if df.close[i]>ama[i]:
            signals[i] = 1
        elif df.close[i]<ama[i]:
            signals[i] = -1
    return signals

def ER_signals(array, AdaWin=10):
    absshift = [0]+[abs(array[i] - array[i-1]) for i in range(1, len(array))]
    noise = [0.0001]*AdaWin + [sum(absshift[i-AdaWin:i+1]) for i in range(len(absshift)) if i>=AdaWin]
    # relative moving momentum - signal
    signal = [0.0001]*AdaWin + [(array[i] - array[i-AdaWin]) for i in range(len(array)) if i>= AdaWin]
    # Calculate efficiency ratio
    ER = [signal[i]/noise[i] for i in range(len(signal))]
    return ER

def AMA(array, TimeperiodLong =30, TimeperiodShort =2, AdaWin =10, matype =1):
    """
    : array: input:  
    : TimeperiodLong : long time period
    : TimeperiodShort : short time period
    : AdaWin : adaptive window length
    : matype == 1: AMA with EMA ,
    : matype == 2: AMA with SMA
    : return res: AMA sequence of an array
    """
    res = np.zeros (array.shape)
    # absolute moving momentum - noise
    ER = ER_signals(array, AdaWin)
    if matype == 1: # AMA by EMA
        slowSC = 2*1./( TimeperiodLong +1 ) # e.g. , 2/31
        fastSC = 2*1./( TimeperiodShort +1 ) # e.g. , 2/3
        diffSC = fastSC - slowSC
        for i, closeData in enumerate(array):
            if i==0:
                res[i] = array[i]
                continue
            er_this = abs(ER[i])
            # mimicking EMA
            scaledSC = pow(slowSC + er_this *diffSC, 2)
            res[i] = res[i-1] + scaledSC *(array[i] - res[i-1])
    elif matype==2: # AMA by SMA
        for i,closeData in enumerate(array):
            if i< TimeperiodLong:
                res[i] = array[i]
                continue
        try:
            finalperiod = TimeperiodShort + abs(ER[i]*(TimeperiodLong - TimeperiodShort))
            finalperiod = int(finalperiod)
        except:
            finalperiod = TimeperiodShort
        res[i] = np.mean(array[i-finalperiod:i+1])
    else :
        pass
    return res
