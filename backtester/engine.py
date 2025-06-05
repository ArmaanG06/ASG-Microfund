import pandas as pd
from backtesting import Backtest, Strategy

class GenericBacktestEngine:
    def __init__(self, data: pd.DataFrame, strategy_cls, strategy_kwargs: dict = None, cash: float = 10000, commission: float = 0.002):
        """
        Initializes the backtest engine.

        :param data: Historical OHLCV DataFrame.
        :param strategy_cls: A class inheriting from backtesting.Strategy.
        :param strategy_kwargs: Optional kwargs to be passed to the strategy.
        :param cash: Starting cash for the backtest.
        :param commission: Commission per trade (e.g., 0.002 = 0.2%).
        """
        self.data = data
        self.strategy_cls = strategy_cls
        self.strategy_kwargs = strategy_kwargs or {}
        self.cash = cash
        self.commission = commission
        

    def run(self):
        """
        Runs the backtest and returns results.
        """
        bt = Backtest(
            self.data,
            self.strategy_cls,
            cash=self.cash,
            commission=self.commission
        )
        stats = bt.run(**self.strategy_kwargs)
        return stats

    def plot(self):
        """
        Plots the results using backtesting.py's built-in plot function.
        """
        bt = Backtest(
            self.data,
            self.strategy_cls,
            cash=self.cash,
            commission=self.commission
        )
        bt.run(**self.strategy_kwargs)
        bt.plot()


