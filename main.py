from portfolio.construction import Portfolio


opt_params = [20, 2.0, 10, 70, 30]

mean_tickers = ['TSLA', 'AMZN', 'HD', 'WMT']
factor_tickers = ['NVDA', 'AAPL', 'JPM', 'TD', 'F', 'UNH']
port = Portfolio('2020-01-01', '2025-01-01', 0.02, 1000000, mean_tickers, factor_tickers)
mean_reversion_summary, momentum_summary, factor_summary, final_metrics = port.backtest_portfolio()

print("------------------")
print(mean_reversion_summary)
print("------------------")
print(momentum_summary)
print("------------------")
print(factor_summary)
print("------------------")
print(final_metrics)
print("------------------")

