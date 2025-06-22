from data.data_loader import data_loader
from backtester.engine import GenericBacktestEngine
from Strategies.mean_reversion import mean_reversion_strategy
from portfolio.benchmark import benchmark
from reporting.generate_report import generate_report
import pandas as pd
from Strategies.factor_investing import factor_investing_screener, factor_investing_strategy




#generate_report(mean_reversion_strategy, start_date="2024-01-01", end_date="2025-01-01")

"""
dl = data_loader()
tickers = ['NVDA', 'JPM', "F", 'UNH']
screener = factor_investing_screener(dl, tickers)
top_stocks = screener.choose_stocks(top_n=10)
print(top_stocks[['ticker', 'composite_score']])
"""

dl = data_loader()
screener = factor_investing_screener(dl, tickers=['NVDA', 'UNH', 'JPM', 'F'])
strategy = factor_investing_strategy("2023-01-01", "2025-01-01", commission=0.01, screener=screener, data_loader=dl)

pf = strategy.backtest()
strategy.plot_performance()
metrics = strategy.get_metrics()
print(metrics)
