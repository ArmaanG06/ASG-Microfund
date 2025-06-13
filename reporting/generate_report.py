import os
import jinja2
import datetime as datetime
from data.data_loader import data_loader
from backtester.engine import GenericBacktestEngine
from portfolio.benchmark import benchmark
import pandas as pd
from statistics import mean, median
import numpy as np



def generate_report(strategy, start_date, end_date):
    """
    Generates an HTML performance report for a strategy over a given time range.
    
    Parameters:
        strategy (object): The strategy instance.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    """

    # Set up the Jinja2 environment
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )

    try:
        template = template_env.get_template("monthly_report_template.html")
    except jinja2.TemplateNotFound:
        raise FileNotFoundError("Template 'monthly_report_template.html' not found in ./reporting/templates")

    strategy_name = strategy.__name__

    dt = data_loader()
    sp500_dict = dt.get_sp500_data(start_date, end_date)
    if strategy_name == "mean_reversion_strategy":
        
        opt_params = [20, 2.0, 10, 0, 100]
        engine = GenericBacktestEngine(
                strategy_cls=strategy,
                strategy_kwargs={'length': opt_params[0], 'std': opt_params[1], 'RSI_upper': opt_params[3], 'RSI_lower': opt_params[4], 'RSI_length': opt_params[2]},
                cash=10000,
                commission=0.000
            )    
        results = engine.batch_backtest(sp500_dict)

    summary_stats = _get_strategy_stats(results)
    bchmk = benchmark(start_date, end_date)
    benchmark_ticker = '^GSPC'
    benchmark_stats = bchmk.get_metrics()
    benchmark_summary_stats = _get_benchmark_stats(benchmark_stats)

    output_dir = os.path.join("reporting", "reports")
    os.makedirs(output_dir, exist_ok=True)

    output_filename = f"{strategy_name}-{start_date}--{end_date}.html"
    output_path = os.path.join(output_dir, output_filename)

    rendered_html = template.render(
        strategy_name=strategy_name,
        summary_stats=summary_stats,
        benchmark_summary_stats=benchmark_summary_stats,
        benchmark_ticker=benchmark_ticker,
        start_date=start_date,
        end_date=end_date
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"✅ Report generated and saved to {output_path}")
    


def _get_strategy_stats(results, metrics=None):
    """
    Compute average and median statistics for a trading strategy.

    Parameters:
        results (dict): A dictionary where keys are tickers and values are dicts of metric results.
        metrics (list, optional): List of metric keys to compute stats on. Defaults to common ones.

    Returns:
        dict: Summary stats with avg and median for each metric, and traded stock count.
    """

    # Default metrics if not provided
    if metrics is None:
        metrics = ['Return [%]', 'CAGR [%]', 'Sharpe Ratio', 'Max. Drawdown [%]']

    metric_values = {metric: [] for metric in metrics}
    traded_stocks = 0

    sorted_results = sorted(results.items(), key=lambda x: x[1]['Return [%]'], reverse=True)

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

    summary_stats['Traded Stocks'] = traded_stocks

    return summary_stats


def _get_benchmark_stats(stats, metrics=None):
    if metrics is None:
        metrics = ['Return [%]', 'CAGR [%]', 'Sharpe Ratio', 'Max. Drawdown [%]']
    
    benchmark_metric_values = {metric: [] for metric in metrics}

    for metric in metrics:
        benchmark_metric_values[metric] = float(stats[metric])

    return benchmark_metric_values