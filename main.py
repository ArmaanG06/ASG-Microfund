from data.data_loader import data_loader
from backtester.engine import GenericBacktestEngine
from Strategies.mean_reversion import mean_reversion_strategy
from portfolio.benchmark import benchmark
import pandas as pd


def test_sp500():
    dt = data_loader()
    sp500_dict = dt.get_sp500_data('2024-01-01', '2025-01-01')

    engine = GenericBacktestEngine(mean_reversion_strategy)
    results = engine.batch_backtest(sp500_dict)

    sorted_results = sorted(results.items(), key=lambda x: x[1]['Return [%]'], reverse=True)
    for ticker, stat in sorted_results:
        print(f"{ticker}: {stat['Return [%]']:.2f}%")


    num = 0
    total = 0
    for ticker, stat in sorted_results:
        total += stat['Return [%]']
        num += 1
        print(f"{ticker}: {stat['Return [%]']:.2f}%")

    avg = total/num
    print(avg)

def test_stock():
    opt_params = [20, 2.0, 10, 0, 100]
    dt = data_loader()
    data = dt.get_data("TSLA", '2023-01-01', '2025-06-01')


    engine = GenericBacktestEngine(
        strategy_cls=mean_reversion_strategy,
        strategy_kwargs={'length': opt_params[0], 'std': opt_params[1], 'RSI_upper': opt_params[3], 'RSI_lower': opt_params[4], 'RSI_length': opt_params[2]},
        cash=10000,
        commission=0.000
    )

    results = engine.run(data)
    engine.plot(data)
    print(results)
