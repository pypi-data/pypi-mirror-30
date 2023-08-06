from datetime import datetime, timedelta

from qstrader.extractor import MultithreadedDataBaseExtractor

import time
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size' : 8})
from matplotlib.finance import candlestick2_ohlc
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import pylab
import matplotlib.patches as mpatches

class LiveChart(object):
    def zigzag(self, date, bidhigh, bidlow, bidclose, pct=1):
        ut = 1 + pct / 100
        dt = 1 - pct / 100
        ld = date[0]
        lp = bidclose[ld]
        tr = None
        zzd, zzp = [ld], [lp]
        for ix, ch, cl in zip(date, bidhigh, bidlow):
            # No initial trend
            if tr is None:
                if ch / lp > ut:
                    tr = 1
                elif cl / lp < dt:
                    tr = -1
            # Trend is up
            elif tr == 1:
                # New high
                if ch > lp:
                    ld, lp = ix, ch
                # Reversal
                elif cl / lp < dt:
                    zzd.append(ld)
                    zzp.append(lp)
                    tr, ld, lp = -1, ix, cl
            # Trend is down
            else:
                # New low
                if cl < lp:
                    ld, lp = ix, cl
                # Reversal
                elif ch / lp > ut:
                    zzd.append(ld)
                    zzp.append(lp)
                    tr, ld, lp = 1, ix, ch
        # Extrapolate the current trend
        if zzd[-1] != date[-1]:
            zzd.append(date[-1])
            if tr is None:
                zzp.append(bidclose[zzd[-1]])
            elif tr == 1:
                zzp.append(bidhigh[zzd[-1]])
            else:
                zzp.append(bidlow[zzd[-1]])
        return pd.Series(zzp, index=zzd).reindex(date)

    def rsifunc(self, series, period=14):
        delta = series.diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[period-1]] = np.mean( u[:period])
        u = u.drop(u.index[:(period-1)])
        d[d.index[period-1]] = np.mean( d[:period]) 
        d = d.drop(d.index[:(period-1)])
        rs = pd.stats.moments.ewma(u, com=period-1, adjust=False) / \
             pd.stats.moments.ewma(d, com=period-1, adjust=False)
        return 100 - 100 / (1 + rs)

    def exponential_average(self, values, window):
        weights = np.exp(np.linspace(-1.,0.,window))
        weights /= weights.sum()
        a = np.convolve(values.values, weights) [:len(values)]
        a[:window]=a[window]
        return a

    def macdfunc(self, idx, values, slow=26, fast=12):
        slow = self.exponential_average(values, slow)
        fast = self.exponential_average(values, fast)
        macd = pd.DataFrame(index=idx)
        macd['slow'] = slow
        macd['fast'] = fast
        macd['macd'] = fast-slow
        return macd

    def plot_rsi_indicator(
        self, rsi, indices, rsi_label, ax=None,
        spines_col='#5998ff', rsicolour='w',
        textsize=6, over=80, under=20
    ):
        """
        RSI Indicator

        """
        if ax is None:
            ax = plt.gca()
        ax.axhline(under, color='g', linewidth=0.5)
        ax.axhline(over, color='r', linewidth=0.5)
        ax.fill_between(
            indices, rsi, under, where=(rsi<=under),
            facecolor=rsicolour, edgecolor=rsicolour)
        ax.fill_between(
            indices, rsi, over, where=(rsi>=over),
            facecolor=rsicolour, edgecolor=rsicolour)
        ax.set_yticks([under,over])
        ax.plot(indices, rsi, rsicolour, linewidth=0.5)
        ax.grid(False)
        ax.spines['top'].set_color(spines_col)
        ax.spines['bottom'].set_color(spines_col)
        ax.spines['left'].set_color(spines_col)
        ax.spines['right'].set_color(spines_col)
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        ax.text(
            0.015, 0.90, rsi_label, va='top', color='w',
            transform=ax.transAxes, fontsize=textsize)
        ax.get_xaxis().set_visible(False)
        return ax

    def plot_macd_indicator(
        self, macd, ema, indices, macd_label, ax=None,
        spines_col='#5998ff', macdcolour='w',
        textsize=6, macdlabel='RSI'
    ):
        if ax is None:
            ax = plt.gca()
        ax.plot(indices, macd, 'r-')
        ax.plot(indices, ema, 'b-')
        ax.fill_between(indices, macd-ema,0, alpha=0.5, facecolor='w')
        ax.spines['top'].set_color(spines_col)
        ax.spines['bottom'].set_color(spines_col)
        ax.spines['left'].set_color(spines_col)
        ax.spines['right'].set_color(spines_col)
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        ax.text(
            0.015, 0.90, macd_label, va='top', color='w',
            transform=ax.transAxes, fontsize=textsize)
        return ax

    def plot_price_chart(
        self, popen, phigh, plow, pclose, ax=None, spines_col='#5998ff'
    ):
        ax.grid(True, linestyle='--', linewidth=0.3)
        ax.yaxis.label.set_color('w')
        ax.spines['top'].set_color(spines_col)
        ax.spines['bottom'].set_color(spines_col)
        ax.spines['left'].set_color(spines_col)
        ax.spines['right'].set_color(spines_col)
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        ax.get_xaxis().set_visible(False)
        candlestick2_ohlc(
            ax, popen, phigh, plow, pclose,
            width=1, colorup='#9eff15', colordown='#ff1717')
        return ax
    
    def plot_zigzag(
        self, indices, zigzag, ax=None, spines_col='#5998ff'
    ):
        zig_line = zigzag.interpolate(method='linear')
        ax.plot(indices, zig_line, '-', linewidth=1)
        ax.plot(indices, zigzag, 'o', markersize=3)
        return ax
    
    def get_data(self, symbol):
        end = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=1)# datetime(2017,12,30,0,0)
        start = end - timedelta(minutes=60) #datetime(2017,,1,0,0)
        tf = 'm1'
        x = MultithreadedDataBaseExtractor(
                symbol, tf, start, end).data_ready[start:end]

        return symbol, x.index, x.bidopen, x.bidhigh, x.bidlow, x.bidclose, x.volume

    def graph(self, symbol, spines_col='#5998ff', figcolor='#07000d'):
        """
        """
        fig.clf()
        symbol, date, bidopen, bidhigh, bidlow, bidclose, volume = self.get_data(symbol)
        # Date function
        def format_date(x, pos=None):
            thisind = np.clip(int(x + 0.5), 0, N - 1)
            return date[thisind].strftime('%Y-%m-%d %H:%M')
        N = len(date)
        indices = np.arange(len(date))
        # Indicators
        # RSI
        period = 14
        rsi_label = 'RSI (%s)' % period
        rsi = self.rsifunc(bidclose, period=period).reindex(date).values
        # MACD
        maslow = 26
        mafast = 12
        ema = 9
        macd_label = "MACD (%s, %s, %s)" % (maslow, mafast, ema)
        m = self.macdfunc(date, bidclose, maslow, mafast)
        macd = m.macd
        ema = self.exponential_average(macd, ema)
        # ZigZag
        zigga = self.zigzag(date, bidhigh, bidlow, bidclose, pct=0.1)
        # Define artists
        ax_ohlc = plt.subplot2grid(
            (6,4),(0,0), rowspan=4, colspan=4,facecolor='#07000d')
        ax_macd = plt.subplot2grid(
            (6,4), (5,0), sharex=ax_ohlc, rowspan=1,
            colspan=4, axisbg='#07000d')
        ax_rsi = plt.subplot2grid(
            (6,4),(4,0), sharex=ax_ohlc, rowspan=1,
            colspan=4, facecolor='#07000d')
        # Plot charts
        self.plot_price_chart(
            bidopen, bidhigh, bidlow, bidclose, ax=ax_ohlc)
        self.plot_zigzag(indices, zigga, ax=ax_ohlc)
        self.plot_rsi_indicator(rsi, indices, rsi_label, ax=ax_rsi)
        self.plot_macd_indicator(macd, ema, indices, macd_label, ax=ax_macd)
        # Tidy updates
        ax_macd.xaxis.set_major_formatter(mticker.FuncFormatter(format_date))
        for label in ax_macd.xaxis.get_ticklabels():
            label.set_rotation(45)  
        fig.autofmt_xdate()
        # Layout customistion
        plt.subplots_adjust(
            left=.10, bottom=.19, right=.93, top=.94, wspace=.20, hspace=.07)
        # Plot Labels 
        plt.suptitle(symbol+' Price Action', color='w')
        plt.ylabel('Price')
        # Legend
        plt.legend(loc=9, ncol=2, prop={'size':7}, fancybox=True, borderaxespad=0.)

fig = plt.figure(facecolor='#07000d')

def animate(i):
    LiveChart().graph('USDCAD')
      
while True:
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()
    

