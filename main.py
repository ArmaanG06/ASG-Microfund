from data.data_loader import data_loader
from backtester.engine import GenericBacktestEngine
from Strategies.mean_reversion import mean_reversion_strategy


loader = data_loader()
tsla = loader.get_data("TSLA", '2020-01-01', '2025-06-01')
bt = GenericBacktestEngine(tsla, mean_reversion_strategy, cash=10000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()
