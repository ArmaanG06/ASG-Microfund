from portfolio.construction import Portfolio

mean_tickers = ['TSLA', 'TSLL', 'SOXL']
factor_tickers = ['NVDA', 'AAPL', 'JPM', 'TD', 'F', 'UNH', 'AMZN', ]
port = Portfolio('2020-01-01', '2025-01-01', 0.02, 1000000, mean_tickers, factor_tickers)
mean_reversion_summary, momentum_summary, factor_summary, final_metrics = port.backtest_portfolio()

print("---------mean_reversion_summary---------")
for metric, dict in mean_reversion_summary.items():
    print(f"{metric}: {dict['avg']}, ", end='')
    print()
print("---------momentum_summary---------")
print(momentum_summary)
print("--------factor_summary----------")
print(factor_summary)
print("--------final_metrics----------")
print(final_metrics)
print("------------------")
