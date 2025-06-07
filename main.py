from data.data_loader import data_loader
from backtester.engine import GenericBacktestEngine
from Strategies.mean_reversion import mean_reversion_strategy
import pandas as pd


dt = data_loader()
sp500_dict = dt.get_sp500_data('2024-01-01', '2025-01-01')

engine = GenericBacktestEngine(mean_reversion_strategy)
results = engine.batch_backtest(sp500_dict)

sorted_results = sorted(results.items(), key=lambda x: x[1]['Return [%]'], reverse=True)
for ticker, stat in sorted_results[:10]:
    print(f"{ticker}: {stat['Return [%]']:.2f}%")


num = 0
total = 0
for ticker, stat in sorted_results:
    total += stat['Return [%]']
    num += 1
    print(f"{ticker}: {stat['Return [%]']:.2f}%")

avg = total/num
print(avg)