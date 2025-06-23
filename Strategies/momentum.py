from data.data_loader import data_loader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class momentum_strategy():

    LOOKBACK_WINDOWS = [12,6,3]

    def __init__(self, start_date, end_date, equity, commission: float=0.02, index:str="^GSPC", LOOKBACK_WINDOWS: list=[12,6,3]):
        self.start_date = start_date
        self.end_date = end_date
        self.index = index
        self.LOOKBACK_WINDOWS = LOOKBACK_WINDOWS
        self.commission = commission/100
        self.equity = equity

    def _get_data(self):
        dl = data_loader()
        df = dl.get_sp500_data_df(start=self.start_date, end=self.end_date)
        mtl = (df.pct_change() + 1 )[1:].resample("ME").prod()
        return mtl
    
    def _get_rolling_returns(self, mtl, a, b, c):
        f = lambda x: np.prod(x) - 1
        return mtl.rolling(a).apply(f), mtl.rolling(b).apply(f), mtl.rolling(c).apply(f)
    

    def _plot_pf(self, strat_pf):
        plt.figure(figsize=(12, 6))
        plt.plot(strat_pf, label='Momentum Strategy', linewidth=2)
        plt.title(f'Momentum Strategy')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _metrics(self, pf_series, risk_free_rate=0.0):
        df = pf_series.copy()
        df = df.dropna()
        
        start = df.index[0]
        end = df.index[-1]
        duration = end - start

        returns = df.pct_change().dropna()
        cumulative_return = df[-1] / df[0] - 1
        n_years = (df.index[-1] - df.index[0]).days / 365.25

        cagr = (df[-1] / df[0])**(1/n_years) - 1
        ann_vol = returns.std() * np.sqrt(12)
        sharpe = (cagr - risk_free_rate) / ann_vol if ann_vol != 0 else np.nan

        downside_returns = returns.copy()
        downside_returns[downside_returns > 0] = 0
        sortino = (cagr - risk_free_rate) / (downside_returns.std() * np.sqrt(12)) if downside_returns.std() != 0 else np.nan

        running_max = df.cummax()
        drawdown = (df - running_max) / running_max
        max_dd = drawdown.min()
        avg_dd = drawdown.mean()

        # Calmar Ratio = CAGR / Max Drawdown (abs value)
        calmar = cagr / abs(max_dd) if max_dd != 0 else np.nan

        # Drawdown duration
        dd_durations = []
        in_drawdown = False
        dd_start = None

        for date, val in drawdown.items():
            if val < 0:
                if not in_drawdown:
                    in_drawdown = True
                    dd_start = date
            elif in_drawdown:
                in_drawdown = False
                dd_end = date
                dd_durations.append(dd_end - dd_start)

        if in_drawdown:
            dd_durations.append(df.index[-1] - dd_start)

        max_dd_duration = max(dd_durations) if dd_durations else pd.Timedelta(0)
        avg_dd_duration = sum(dd_durations, pd.Timedelta(0)) / len(dd_durations) if dd_durations else pd.Timedelta(0)

        metrics = {
            "Start": start,
            "End": end,
            "Duration": duration,
            "Exposure Time [%]": 100.0,
            "Equity Final [$]": df.iloc[-1] * self.equity,
            "Equity Peak [$]": df.max() * self.equity,
            "Return [%]": cumulative_return * 100,
            "Buy & Hold Return [%]": cumulative_return * 100,
            "Return (Ann.) [%]": cagr * 100,
            "Volatility (Ann.) [%]": ann_vol * 100,
            "CAGR [%]": cagr * 100,
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Calmar Ratio": calmar,
            "Alpha [%]": 0.0,  # Requires benchmark comparison
            "Beta": 1.0,       # Requires benchmark comparison
            "Max. Drawdown [%]": max_dd * 100,
            "Avg. Drawdown [%]": avg_dd * 100,
            "Max. Drawdown Duration": max_dd_duration,
            "Avg. Drawdown Duration": avg_dd_duration
        }

        return pd.Series(metrics)

        
    def run(self):

        mtl = self._get_data()
        ret_12, ret_6, ret_3 = self._get_rolling_returns(mtl, self.LOOKBACK_WINDOWS[0], self.LOOKBACK_WINDOWS[1], self.LOOKBACK_WINDOWS[2])
        returns = []
        if len(mtl) < 13:
            raise ValueError("Not enough data to compute momentum strategy.")
            return
        else:
            for i in range(12, len(mtl)-1):
                date = mtl.index[i]
                next_date = mtl.index[i+1]

                top_50 = ret_12.iloc[i-1].nlargest(30).index
                top_30 = ret_6.iloc[i-1][top_50].nlargest(30).index
                top_10 = ret_3.iloc[i-1][top_30].nlargest(10).index

                monthly_ret = mtl.loc[next_date, top_10].mean()
                returns.append(monthly_ret * (1-self.commission))

            strat_pf = pd.Series(returns, index=mtl.index[13:]).cumprod()
            metrics = self._metrics(strat_pf)
            return metrics
