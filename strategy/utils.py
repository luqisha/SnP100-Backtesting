from strategy.keltner import *
from strategy.moving_average import *
from strategy.rsi import *
from strategy.MACD import *
import os
from datetime import datetime as dt

def asset_df(symbol):
    asset_dir = os.path.join(os.path.expanduser('~'), 'trading/zipline-technical-analysis/data/dse/')
    df = pd.read_csv(asset_dir + '/daily/' + str(symbol) + '.csv')
    return df.set_index(pd.DatetimeIndex(df.timestamp))

def combined_rets(stocks=[]):
    master = pd.DataFrame(asset_df(stocks[0])["close"])
    for stock in stocks[1:]:
        master[stock] = asset_df(stock).close
    master.rename(columns={'close':stocks[0]}, inplace=True)
    return master

def signal_generator(symbol, keltner_window=90, ma_long=40, ma_short=4, ad_window=4, rsitype=1, rsi_window=7, rsi_diff=0.0001, downmult=0.8, upmult=0.8, gradient_window=7):
    ohlc = asset_df(symbol)
    
    # keltner_signals(df, span, strategy=1, TimeperiodLong =40, TimeperiodShort =4, AdaWin =4)
    keltner_sigs = keltner_signals(ohlc, keltner_window, strategy=3, TimeperiodLong =ma_long, TimeperiodShort =ma_short, AdaWin =ad_window)
    
    #  RSI_signals(data, downThres =30 , upperThres =70, DiffRate =0.0024 , rsitype =1 , SMA=[], SMArate =0.001, window=14, downmult=0.5, upmult=1):
    rsi_sigs = RSI_signals(ohlc,downmult=downmult, upmult=upmult, rsitype=rsitype, window=rsi_window, DiffRate= rsi_diff)
    
    # MACD signals : macd_signals(df, short_period, long_period, signal_period):
    macd_sigs = macd_signals(ohlc, short_period=12, long_period=26, signal_period=9)
   
    slist = pd.DataFrame({"close" : ohlc.close, "keltner" : keltner_sigs, "RSI" : rsi_sigs, "macd" : macd_sigs})
    
    # Working with the gradient
    slist["gradient"] = (slist.close-slist.close.shift(2))/2
    buys = [1 if (round(slist.gradient[i], 1)==0) and min([slist.gradient[j] for j in range(i-gradient_window,i)])<-0.6 else 0 for i in range(len(slist.index))]
    sells = [-1 if (round(slist.gradient[i], 1)==0) and max([slist.gradient[j] for j in range(i-gradient_window,i)])>0.6 else 0 for i in range(len(slist.index))]
    slist.gradient = [b+s for b,s in zip(buys,sells)]
    
    slist['signal'] = slist[['keltner', 'RSI', 'gradient']].sum(axis=1)
    # Efficiency ratio
    slist['ER'] = ER_signals(ohlc.close, ad_window)
    return slist


def signals_plot(slist, signal="gradient", er_adj=True):
    
    signals = slist.signal
    
    if er_adj==True:
        buys = [slist.close[i] if (slist[signal][i]>0) and (slist.ER[i]<0.4) else None for i in range(len(signals))]
        sells = [slist.close[i] if (slist[signal][i]<0) and (slist.ER[i]>0) else None for i in range(len(signals))]
    else:
        buys = [slist.close[i] if (slist[signal][i]>0) else None for i in range(len(signals))]
        sells = [slist.close[i] if (slist[signal][i]<0) else None for i in range(len(signals))]
    
    plt.figure(figsize=(15,10))
    plt.plot(slist.close, label="price", color="black")
    plt.plot(slist.index, buys, 'bo')
    plt.plot(slist.index, sells, 'ro')

    plt.legend()
    print(f'Buycount:{sum([1 for x in buys if x!=None])}, Sellcount:{sum([1 for x in sells if x!=None])}')
    
def plot_signals(signals, ohlc):
    
    buys = [ohlc.close[i] if (signals[i]>0) else None for i in range(len(signals))]
    sells = [ohlc.close[i] if (signals[i]<0) else None for i in range(len(signals))]
    
    plt.figure(figsize=(16,8))
    plt.plot(ohlc.close, label="price", color="black")
    plt.plot(ohlc.index, buys,'bo', label="buys")
    plt.plot(ohlc.index, sells, 'ro', label="sells")

    plt.legend()
    print(f'Buycount:{sum([1 for x in buys if x!=None])}, Sellcount:{sum([1 for x in sells if x!=None])}')