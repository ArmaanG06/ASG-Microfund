import os
import jinja2
import datetime as datetime
from portfolio.construction import Portfolio
from statistics import mean, median
import pdfkit
from bs4 import BeautifulSoup
import imgkit
import os

def _render_html(start_date, end_date,risk, time, mean_tickers, factor_tickers, commissions, cash):

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

    port = Portfolio('2020-01-01', '2025-01-01', commissions, cash, mean_tickers, factor_tickers, risk,  time)
    mean_reversion_summary, momentum_summary, factor_summary, final_metrics, benchmark_summary, returns_df= port.backtest_portfolio()
    factor_plot_dir, mom_plot_dir, mean_plot_dir, equity_curve_path, daily_return_path = port.plot_stratgies()

    benchmark_metrics_summary = {'Return [%]': benchmark_summary['Return [%]'], 'CAGR [%]': benchmark_summary['CAGR [%]'], 'Sharpe Ratio': benchmark_summary['Sharpe Ratio'], 'Max. Drawdown': benchmark_summary['Max. Drawdown [%]']}


    factor_plot_path_web = os.path.relpath(factor_plot_dir, start=os.path.dirname(output_path)).replace('\\', '/')
    momentum_plot_path_web = os.path.relpath(mom_plot_dir, start=os.path.dirname(output_path)).replace('\\', '/')
    mean_plot_web = os.path.relpath(mean_plot_dir, start=os.path.dirname(output_path)).replace("\\", "/")
    equity_curve_plot_web = os.path.relpath(equity_curve_path, start=os.path.dirname(output_path)).replace("\\", "/")
    daily_returns_plot_web = os.path.relpath(daily_return_path, start=os.path.dirname(output_path)).replace("\\", "/")


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
        mean_plot_dir=mean_plot_web,
        equity_curve_dir=equity_curve_plot_web,
        daily_return_dir=daily_returns_plot_web
    )
    return rendered_html, output_path

def generate_report(start_date, end_date, risk, time, mean_tickers, factor_tickers, commissions, cash):
    """
    Generates an HTML performance report for a strategy over a given time range.
    
    Parameters:
        strategy (object): The strategy instance.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    """

    # Set up the Jinja2 environment
    
    rendered_html, output_path= _render_html(start_date, end_date, risk, time, mean_tickers, factor_tickers, commissions, cash)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    
    print(f"✅ Report generated and saved to {output_path}")

def generate_pdf(start_date, end_date, risk, time):
    """
    Generates a PDF performance report for a strategy over a given time range.
    
    Parameters:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        risk (float): Risk parameter for the portfolio.
        time (str): Time horizon for the strategies.
    """
    # First render the HTML content
    rendered_html, html_output_path = _render_html(start_date, end_date, risk, time)
    
    # Set up output directory for PDF
    output_dir = os.path.join("docs", "external")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF output path
    pdf_output_filename = f"ASG Microfund - {start_date} to {end_date}.pdf"
    pdf_output_path = os.path.join(output_dir, pdf_output_filename)
    
    # Options for PDF generation
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'quiet': '',
        'no-outline': None,
        'enable-local-file-access': None  # Required to access local images
    }
    config =imgkit.config(wkhtmltoimage=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe")

    try:
        # Generate PDF from the HTML string
        pdfkit.from_string(rendered_html, pdf_output_path, options=options, configuration=config)
        print(f"✅ PDF report generated and saved to {pdf_output_path}")
        return pdf_output_path
    except Exception as e:
        print(f"❌ Failed to generate PDF report: {str(e)}")
        raise