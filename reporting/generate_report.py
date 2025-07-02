import os
import jinja2
import datetime as datetime
from portfolio.construction import Portfolio
import pandas as pd
from statistics import mean, median
import numpy as np
#from weasyprint import HTML




def generate_report(start_date, end_date):
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

    output_dir = os.path.join("reporting", "reports")
    os.makedirs(output_dir, exist_ok=True)

    output_filename = f"ASG Microfund - {start_date} to {end_date}.html"
    output_path = os.path.join(output_dir, output_filename)

    mean_tickers = ['CL=F']
    factor_tickers = ['NVDA', 'AAPL', 'JPM', 'TD', 'F', 'UNH', 'AMZN', ]
    port = Portfolio('2020-01-01', '2025-01-01', 0.001, 1000000, mean_tickers, factor_tickers)
    mean_reversion_summary, momentum_summary, factor_summary, final_metrics, benchmark_summary= port.backtest_portfolio()
    factor_plot_dir, mom_plot_dir, mean_plot_dir = port.plot_stratgies()
    benchmark_metrics_summary = {'Return [%]': benchmark_summary['Return [%]'], 'CAGR [%]': benchmark_summary['CAGR [%]'], 'Sharpe Ratio': benchmark_summary['Sharpe Ratio'], 'Max. Drawdown': benchmark_summary['Max. Drawdown [%]']}


    factor_plot_path_web = os.path.relpath(factor_plot_dir, start=os.path.dirname(output_path)).replace('\\', '/')
    momentum_plot_path_web = os.path.relpath(mom_plot_dir, start=os.path.dirname(output_path)).replace('\\', '/')
    mean_plot_web = os.path.relpath(mean_plot_dir, start=os.path.dirname(output_path)).replace("\\", "/")


    rendered_html = template.render(
        mean_reversion_summary=mean_reversion_summary,
        momentum_summary=momentum_summary,
        factor_summary = factor_summary,
        final_metrics = final_metrics,
        benchmark_summary = benchmark_metrics_summary,
        mean_tickers = mean_tickers,
        factor_tickers = factor_tickers,
        start_date=start_date,
        end_date=end_date,
        factor_plot_dir=factor_plot_path_web,
        mom_plot_dir=momentum_plot_path_web,
        mean_plot_web=mean_plot_web
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    #HTML(output_path).write_pdf(output_path.replace(".html", ".pdf"))

    print(f"✅ Report generated and saved to {output_path}")
    