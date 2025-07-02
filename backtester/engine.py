import pandas as pd
from backtesting import Backtest
import os

class GenericBacktestEngine:
    def __init__(self, strategy_cls, strategy_kwargs: dict = None, cash: float = 10000, commission: float = 0.002):
        """
        Initializes the backtest engine.

        :param data: Historical OHLCV DataFrame.
        :param strategy_cls: A class inheriting from backtesting.Strategy.
        :param strategy_kwargs: Optional kwargs to be passed to the strategy.
        :param cash: Starting cash for the backtest.
        :param commission: Commission per trade (e.g., 0.002 = 0.2%).
        """
        self.strategy_cls = strategy_cls
        self.strategy_kwargs = strategy_kwargs
        self.cash = cash
        self.commission = commission

    def run(self, data: pd.DataFrame):
        """
        Runs the backtest and returns results.
        """
        
        bt = Backtest(
            data,
            self.strategy_cls,
            cash=self.cash,
            commission=self.commission
        )
        stats = bt.run()
        return stats

    def plot(self, data: pd.DataFrame):
        """
        Plots the results using backtesting.py's built-in plot function.
        Saves the output as an HTML file and returns the relative path.
        """

        strategy = self.strategy_cls.__name__
        start_date = str(data.index[0])[:10]
        end_date = str(data.index[-1])[:10]

        plot_filename = f"{strategy}_{start_date}--{end_date}.html"
        plot_path = os.path.join("reporting", "charts", plot_filename)

        bt = Backtest(
            data,
            self.strategy_cls,
            cash=self.cash,
            commission=self.commission
        )
        bt.run(**(self.strategy_kwargs or {}))

        bt.plot(filename=plot_path, open_browser=False)

        return plot_path

    def batch_backtest(self, data_dict: dict):
        """
        Run backtests on a dict of ticker: DataFrame pairs.
        Returns a dict of ticker: stats
        """
        results = {}
        for ticker, data in data_dict.items():
            try:
                stats = self.run(data)
                results[ticker] = stats
            except Exception as e:
                print(f"Failed on {ticker}: {e}")
        return results
