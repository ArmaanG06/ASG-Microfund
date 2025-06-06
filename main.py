from data.data_loader import data_loader
from backtester.engine import GenericBacktestEngine
from Strategies.mean_reversion import mean_reversion_strategy

dt = data_loader()
data = dt.get_data("TSLA", '2023-01-01', '2025-06-01')
print(data)
"""
#Fix index issues
data.index = data['Date']
del data['Date']
data.index.name = 'Date'
"""
engine = GenericBacktestEngine(
    data=data,
    strategy_cls=mean_reversion_strategy,
    strategy_kwargs={'length': 20, 'std': 2.0},
    cash=10000,
    commission=0.000
)

results = engine.run()
engine.plot()
print(results)
