import os
import jinja2
import datetime as datetime
from portfolio.construction import Portfolio
from statistics import mean, median
import pdfkit
from bs4 import BeautifulSoup
import imgkit
import os

def _render_html(start_date, end_date):

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
    factor_tickers = ['NVDA', 'AAPL', 'JPM', 'TD', 'F', 'UNH', 'AMZN']
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
    return rendered_html, output_path

def generate_report(start_date, end_date):
    """
    Generates an HTML performance report for a strategy over a given time range.
    
    Parameters:
        strategy (object): The strategy instance.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    """

    # Set up the Jinja2 environment
    
    rendered_html, output_path= _render_html(start_date, end_date)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    
    print(f"✅ Report generated and saved to {output_path}")

def generate_pdf(start_date, end_date):
    

    # Step 1: Get the HTML and output path
    rendered_html, _ = _render_html(start_date, end_date)

    # Step 2: Parse the iframe src from rendered HTML
    soup = BeautifulSoup(rendered_html, 'html.parser')
    iframe = soup.find('iframe')
    if not iframe or not iframe.get('src'):
        raise ValueError("No iframe found in rendered HTML.")

    iframe_src = iframe['src']  # e.g., 'reporting/charts/mean_reversion_strategy_2020-01-01--2025-01-01.html'

    # Correct the path to 'reporting/charts' directory (strip extra 'reporting')
    iframe_path = os.path.join(os.path.dirname(__file__), "reports", f'ASG Microfund - {start_date} to {end_date}.html')

    # Step 3: Check if the iframe source file exists
    if not os.path.isfile(iframe_path):
        raise OSError(f"Iframe source file not found: {iframe_path}")

    # Step 4: Convert the iframe HTML to PNG
    png_output_dir = os.path.join("reporting", "charts")
    os.makedirs(png_output_dir, exist_ok=True)

    png_filename = os.path.basename(iframe_src).replace(".html", ".png")
    png_full_path = os.path.join(png_output_dir, png_filename)

    # Configure imgkit to use wkhtmltoimage explicitly if not in the PATH
    config = imgkit.config(wkhtmltoimage=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe")

    # Convert the iframe HTML to PNG
    imgkit.from_file(iframe_path, png_full_path, config=config)

    # Step 5: Compute relative path for PDF embedding
    rel_png_path = os.path.relpath(png_full_path, start=os.path.join("docs", "external")).replace("\\", "/")
    img_tag = soup.new_tag("img", src=rel_png_path, alt="Mean Reversion Performance Chart", style="width:100%; max-width:900px;")

    # Step 6: Replace iframe with <img>
    iframe.replace_with(img_tag)
    modified_html = str(soup)

    # Step 7: Generate PDF
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdf_output_path = os.path.join("docs", "external", f"ASG Microfund - {start_date} to {end_date}.pdf")
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)

    options = {
        'enable-local-file-access': None,
        'quiet': ''
    }

    # Step 8: Generate the PDF
    pdfkit.from_string(modified_html, pdf_output_path, configuration=config, options=options)

    print(f"✅ PDF report saved to {pdf_output_path}")