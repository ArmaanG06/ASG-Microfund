from data.data_loader import data_loader
import pandas as pd
import numpy as np
import datetime
from scipy.stats import linregress

class benchmark:

    def __init__(self, start, end, ticker: str = '^GSPC'):
        self.ticker = ticker
        self.start = datetime.datetime.strptime(start, "%Y-%m-%d")
        self.end = datetime.datetime.strptime(end, "%Y-%m-%d")
        dt = data_loader()
        self.benchmark_data = dt.get_data(self.ticker, self.start, self.end)
        self.daily_returns = self.get_daily_returns()
        self.returns_df = self.benchmark_data[['Close']].copy()
        self.returns_df['Returns'] = self.daily_returns
        self.returns_df.dropna(inplace=True)


    def get_daily_returns(self):
        returns = self.benchmark_data['Close'].pct_change().dropna()
        return returns  # Series

    def get_total_return(self):
        start_price = self.benchmark_data['Close'].iloc[0]
        end_price = self.benchmark_data['Close'].iloc[-1]
        return (end_price / start_price) - 1

    def get_metrics(self, risk_free_rate=0.0):
        df = self.returns_df.copy()
        df['Cumulative'] = (1 + df['Returns']).cumprod()
        df['Peak'] = df['Cumulative'].cummax()
        df['Drawdown'] = df['Cumulative'] / df['Peak'] - 1

        duration = self.end - self.start
        total_return = self.get_total_return()
        annualized_return = (1 + total_return) ** (252 / len(df)) - 1
        volatility = df['Returns'].std() * np.sqrt(252)
        cagr = (df['Cumulative'].iloc[-1]) ** (1 / (len(df) / 252)) - 1
        sharpe = (df['Returns'].mean() * 252 - risk_free_rate) / (df['Returns'].std() * np.sqrt(252))
        downside_returns = df[df['Returns'] < 0]['Returns']
        sortino = (df['Returns'].mean() * 252) / (downside_returns.std() * np.sqrt(252)) if not downside_returns.empty else np.nan
        max_dd = df['Drawdown'].min()
        avg_dd = df['Drawdown'][df['Drawdown'] < 0].mean()

        # Drawdown duration
        drawdown_durations = []
        current_dd_duration = 0
        for dd in df['Drawdown']:
            if dd < 0:
                current_dd_duration += 1
            else:
                if current_dd_duration > 0:
                    drawdown_durations.append(current_dd_duration)
                    current_dd_duration = 0
        if current_dd_duration > 0:
            drawdown_durations.append(current_dd_duration)
        max_dd_duration = max(drawdown_durations) if drawdown_durations else 0
        avg_dd_duration = np.mean(drawdown_durations) if drawdown_durations else 0

        # Alpha & Beta vs market (self vs itself here, but you could modify this to compare with another benchmark)
        market_returns = df['Returns']
        slope, intercept, r_value, p_value, std_err = linregress(market_returns, df['Returns'])
        beta = slope
        alpha = (annualized_return - risk_free_rate) - beta * (annualized_return - risk_free_rate)

        return pd.Series({
            'Start': self.start,
            'End': self.end,
            'Duration': duration,
            'Exposure Time [%]': 100.0,  # Always exposed
            'Equity Final [$]': df['Cumulative'].iloc[-1] * 10000,
            'Equity Peak [$]': df['Peak'].max() * 10000,
            'Return [%]': total_return * 100,
            'Buy & Hold Return [%]': total_return * 100,
            'Return (Ann.) [%]': annualized_return * 100,
            'Volatility (Ann.) [%]': volatility * 100,
            'CAGR [%]': cagr * 100,
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino,
            'Calmar Ratio': cagr / abs(max_dd) if max_dd != 0 else np.nan,
            'Alpha [%]': alpha * 100,
            'Beta': beta,
            'Max. Drawdown [%]': max_dd * 100,
            'Avg. Drawdown [%]': avg_dd * 100,
            'Max. Drawdown Duration': pd.Timedelta(days=int(max_dd_duration)),
            'Avg. Drawdown Duration': pd.Timedelta(days=int(avg_dd_duration)),
        })
