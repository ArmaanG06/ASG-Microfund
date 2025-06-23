from portfolio.benchmark import benchmark
from portfolio.risk_management import RiskManagement
import pandas as pd
import numpy as np
from Strategies.factor_investing import factor_investing_strategy, factor_investing_screener
from Strategies.momentum import momentum_strategy
from Strategies.mean_reversion import mean_reversion_strategy
from backtester.engine import GenericBacktestEngine
from data.data_loader import data_loader

class Portfolio:

    def __init__(self, start, end, commissions, cash, mean_tickers, factor_tickers):
        user_tolerance = input("What is your risk tolerance (low, medium, or high): ")
        user_time = input("What is your investment time horizon (long, medium, or short): ")
        self.risk_manager = RiskManagement(user_tolerance, user_time)

        self.mean_alloc, self.momentum_alloc, self.factor_alloc = self._get_strategy_allocations()

        self.mean_tickers = mean_tickers
        self.factor_tickers = factor_tickers

        self.start = start
        self.end = end
        self.commissions = commissions
        self.cash = cash

        self.risk_manager = RiskManagement(user_tolerance, user_time)
        self.benchmark = benchmark(start=start, end=end)
        self.data_loader = data_loader()

        self.factor_strategy = factor_investing_strategy(start, end, commissions, self.data_loader, self.factor_tickers)
        self.momentum_strategy = momentum_strategy(start, end, self.momentum_alloc, commissions)
        self.mean_strategy = mean_reversion_strategy


    def _get_strategy_allocations(self):
        risk_profile = self.risk_manager.get_risk_profile()
        mean_alloc = risk_profile['allocations_advanced']['mean_reversion']
        momentum_alloc = risk_profile['allocations_advanced']['momentum']
        factor_alloc = risk_profile['allocations_advanced']['factor_investing']

        return mean_alloc, momentum_alloc, factor_alloc
    
    def backtest_mean(self):
        mean_reversion_results = []
        opt_params = [20, 2.0, 10, 70, 30]

        engine = GenericBacktestEngine(
                    strategy_cls=self.mean_strategy,
                    strategy_kwargs={'length': opt_params[0], 'std': opt_params[1], 'RSI_upper': opt_params[3], 'RSI_lower': opt_params[4], 'RSI_length': opt_params[2]},
                    cash=self.mean_alloc*self.cash,
                    commission=self.commissions
                )    
        data = self.data_loader.get_multiple_data(self.mean_tickers, self.start, self.end)
        mean_reversion_results = engine.batch_backtest(data)

        return mean_reversion_results
    
    def backtest_momentum(self):
        momentum_results = self.momentum_strategy.run()
        return momentum_results
    
    def backtest_factor(self):
        pf = self.factor_strategy.backtest()
        metrics = self.factor_strategy.get_metrics()
        return metrics
    
    def _get_portfolio_results(self, mean_reversion_results, momentum_results, factor_results):

        final_metrics = {}
        metrics = ['Return [%]', 'CAGR [%]', 'Sharpe Ratio', 'Max. Drawdown [%]']

        metric_values = {metric: [] for metric in metrics}
        traded_stocks = 0

        sorted_results = sorted(mean_reversion_results.items(), key=lambda x: x[1]['Return [%]'], reverse=True)
        for ticker, stats in mean_reversion_results.items():
            print(ticker, type(stats), stats)

        for ticker, stat in sorted_results:
            if stat['Return [%]'] != 0:
                traded_stocks += 1
                for metric in metrics:
                    val = stat.get(metric, np.nan)
                    metric_values[metric].append(val)

        summary_stats = {}

        for metric, values in metric_values.items():
            clean_vals = [v for v in values if not (isinstance(v, float) and np.isnan(v))]
            summary_stats[metric] = {
                'avg': np.mean(clean_vals) if clean_vals else np.nan,
                'median': np.median(clean_vals) if clean_vals else np.nan
            }

        mean_reversion_summary =  summary_stats

        momentum_summary = {metric: momentum_results[metric] for metric in metrics if metric in momentum_results}

        factor_summary = factor_results

        for metric in metrics:
            # Extract values from each summary
            mean_val = mean_reversion_summary.get(metric, {}).get('avg', np.nan)
            momentum_val = momentum_summary.get(metric, np.nan)
            factor_val = factor_summary.get(metric, np.nan)

            # Weighted average of available metrics
            weighted_values = [
                mean_val * self.mean_alloc if not np.isnan(mean_val) else 0,
                momentum_val * self.momentum_alloc if not np.isnan(momentum_val) else 0,
                factor_val * self.factor_alloc if not np.isnan(factor_val) else 0
            ]
            total_weight = sum([
                self.mean_alloc if not np.isnan(mean_val) else 0,
                self.momentum_alloc if not np.isnan(momentum_val) else 0,
                self.factor_alloc if not np.isnan(factor_val) else 0
            ])
            final_metrics[metric] = sum(weighted_values) / total_weight if total_weight > 0 else np.nan

        return mean_reversion_summary, momentum_summary, factor_summary, final_metrics


    def backtest_portfolio(self):
        mean_reversion_results = self.backtest_mean()
        momentum_results = self.backtest_momentum()
        factor_results = self.backtest_factor()

        mean_reversion_summary, momentum_summary, factor_summary, final_metrics = self._get_portfolio_results(mean_reversion_results, momentum_results, factor_results)
        return mean_reversion_summary, momentum_summary, factor_summary, final_metrics


    



