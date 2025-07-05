from portfolio.benchmark import benchmark
from portfolio.risk_management import RiskManagement
import pandas as pd
import numpy as np
from Strategies.factor_investing import factor_investing_strategy, factor_investing_screener
from Strategies.momentum import momentum_strategy
from Strategies.mean_reversion import mean_reversion_strategy
from backtester.engine import GenericBacktestEngine
from data.data_loader import data_loader
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick



class Portfolio:

    def __init__(self, start, end, commissions, cash, mean_tickers, factor_tickers, user_tolerance: str='low', user_time: str='medium'):
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
        engine = GenericBacktestEngine(
                    strategy_cls=self.mean_strategy,
                    cash=self.mean_alloc*self.cash,
                    commission=self.commissions
                )    
        data = self.data_loader.get_multiple_data(self.mean_tickers, self.start, self.end)
        mean_reversion_results, pf_ret_dict = engine.batch_backtest(data)
        first_df = list(data.values())[0]
        self.mean_plot_path = engine.plot(first_df)
        
        return mean_reversion_results, pf_ret_dict
    
    def backtest_momentum(self):
        momentum_results, pf_ret = self.momentum_strategy.run()
        return momentum_results, pf_ret
    
    def backtest_factor(self):
        pf_cum, pf_ret = self.factor_strategy.backtest()
        metrics = self.factor_strategy.get_metrics()
        return metrics, pf_ret
    
    def _get_portfolio_results(self, mean_reversion_results, momentum_results, factor_results):

        final_metrics = {}
        metrics = ['Return [%]', 'CAGR [%]', 'Sharpe Ratio', 'Max. Drawdown [%]']

        metric_values = {metric: [] for metric in metrics}
        traded_stocks = 0

        sorted_results = sorted(mean_reversion_results.items(), key=lambda x: x[1]['Return [%]'], reverse=True)
        

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
    

    def returns_df(self, mean_reversion, momentum, factor_investing):
        """
        Combine daily returns from 3 strategies into one aligned DataFrame.
        
        Parameters:
            mean_reversion (dict): Daily returns (only use first).
            momentum (pd.Series): Monthly returns.
            factor_investing (pd.Series): Daily returns.
            
        Returns:
            pd.DataFrame: Combined returns with columns:
                        ['Mean Reversion', 'Factor Investing', 'Momentum']
        """
        
        if not mean_reversion:
            raise ValueError("mean_reversion dictionary is empty")
        
        # Get first mean reversion series
        first_key = next(iter(mean_reversion))
        mean_reversion = pd.Series(mean_reversion[first_key])

        monthly_dates = pd.date_range(start=self.start, periods=len(momentum), freq='ME')
        momentum.index = monthly_dates        
        # Create common index
        start_date = min(
            #momentum.index.min(), 
            mean_reversion.index.min(), 
            factor_investing.index.min()
        )
        end_date = max(
            #momentum.index.max(), 
            mean_reversion.index.max(), 
            factor_investing.index.max()
        )
        full_index = pd.date_range(start=start_date, end=end_date, freq='D')
        
        combined = pd.DataFrame(index=full_index)
        
        combined['Mean Reversion'] = mean_reversion
        combined['Factor Investing'] = factor_investing
        
        
        momentum_daily_value = momentum.reindex(full_index, method='ffill')
        combined['Momentum'] = momentum_daily_value.pct_change().fillna(0)

        combined.dropna(how='any', inplace=True)
        self.combined_results = combined
        return combined
    
    def _plot_daily_returns(self, save_dir="reporting/charts"):
        df_returns = self.combined_results
        allocs = {
        'Mean Reversion': self.cash * self.mean_alloc,
        'Momentum': self.cash * self.momentum_alloc,
        'Factor Investing': self.cash * self.factor_alloc
        }  

        equity_curves = {}
        for strat in df_returns.columns:
            cumulative_return = (1 + df_returns[strat]).cumprod()
            equity_curves[strat] = cumulative_return * allocs[strat]

        df_equity = pd.DataFrame(equity_curves)

        plt.figure(figsize=(12, 6))
        for strat in df_equity.columns:
            plt.plot(df_equity.index, df_equity[strat], label=strat, linewidth=2)
        plt.title("Equity Curve per Strategy")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.legend()

        ax = plt.gca()
        ax.get_yaxis().set_major_formatter(
            mtick.FuncFormatter(lambda x, p: f'${int(x):,}')
        )

        equity_path = os.path.join("reporting", "charts", 'equity_curve.png')
        os.makedirs(os.path.dirname(equity_path), exist_ok=True)
        plt.savefig(equity_path)
        plt.close()
                    
        # --- Plot Daily Returns ---
        plt.figure(figsize=(12, 6))
        for strat in df_returns.columns:
            plt.plot(df_returns.index, df_returns[strat], label=strat, linewidth=1)
        plt.title("Daily Returns per Strategy")
        plt.xlabel("Date")
        plt.ylabel("Daily Return")
        plt.grid(True)
        plt.legend()
        if df_returns.abs().max().max() > 0.2:
            plt.ylim(-0.20, 0.20)

        plt.tight_layout()
        returns_path = os.path.join("reporting", "charts", "daily_returns.png")
        os.makedirs(os.path.dirname(returns_path), exist_ok=True)
        plt.savefig(returns_path)
        plt.close()

        return equity_path, returns_path


    def backtest_portfolio(self):
        mean_reversion_results, mean_returns = self.backtest_mean()
        momentum_results, momentum_returns = self.backtest_momentum()
        factor_results, factor_returns = self.backtest_factor()

        mean_reversion_summary, momentum_summary, factor_summary, final_metrics = self._get_portfolio_results(mean_reversion_results, momentum_results, factor_results)
        benchmark_results = self.benchmark.get_metrics()
        returns_df = self.returns_df(mean_returns, momentum_returns, factor_returns)
        return mean_reversion_summary, momentum_summary, factor_summary, final_metrics, benchmark_results, returns_df


    def plot_stratgies(self):
        factor_plot_path = self.factor_strategy.plot_performance()
        momentum_plot_path = self.momentum_strategy.plot_preformance()
        mean_plot_path = self.mean_plot_path
        equity_curves_path, returns_curve_path = self._plot_daily_returns()
        return factor_plot_path, momentum_plot_path, mean_plot_path, equity_curves_path, returns_curve_path

    




