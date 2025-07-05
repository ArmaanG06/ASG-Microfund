# ASG Microfund

A simulated quantitative investment fund designed to emulate the structure and rigor of a professional hedge fund. Built from scratch using Python, this multi-strategy platform is a showcase of quantitative research, portfolio construction, risk management, and reporting.

---

## Project Overview

**ASG Microfund** is an educational and professional-grade project designed to replicate the internal operations of a quantitative investment fund. The project includes strategy development, backtesting, execution simulation, performance reporting, and an interactive dashboard. It is modular, extensible, and designed for long-term use and experimentation.

---

## Features

* **Multi-strategy Framework:** Supports mean reversion, momentum, and factor-based strategies
* **Modular Portfolio Construction:** Risk-weighted, equal-weighted, or factor-score-based allocations
* **Realistic Backtesting:** Trade costs, commissions, and rebalancing logic
* **Professional Reporting:** PDF and HTML reports with performance metrics, charts, and commentary
* **Streamlit Dashboard:** Interactive visualization and analytics dashboard

---

## Educational Goals

* Apply core concepts from finance, computer science, and mathematics
* Build a fully functioning quant research and trading infrastructure
* Simulate the experience of managing a fund with weekly deliverables
* Serve as a standout portfolio piece and launchpad for quant/dev careers

---

## Strategies Implemented

| Strategy         | Type         | Horizon     | Bias         | Market Suitability |
| ---------------- | ------------ | ----------- | ------------ | ------------------ |
| Mean Reversion   | Technical    | Short-term  | Contrarian   | Sideways/Volatile  |
| Momentum         | Price Action | Medium-term | Trend-Follow | Trending           |
| Factor Investing | Fundamental  | Long-term   | Multi-factor | Stable/Fundamental |

---

## Portfolio & Risk Engine

* Custom portfolio constructor: combine multiple strategies with user-defined weights
* Risk metrics: Sharpe, max drawdown, volatility, rolling alpha/beta
* Execution simulation: slippage, transaction cost modeling, rebalancing logic

---

## Reporting System

* **Reports:** Generated in both HTML and PDF formats
* **Visualizations:** Equity curves, drawdowns, rolling metrics
* **Trade Logs:** Tabular logs for each strategy
* **Template-Driven:** Powered by Jinja2 + wkhtmltopdf

---

## Streamlit Dashboard

* Navigate strategy performance and allocation dynamically
* Plot portfolio NAV, rolling Sharpe, and exposure over time
* Supports user inputs for strategy parameters and dates
* MVP implemented in `/dashboard/streamlit_app.py`

---

## File Structure

```
ASG Microfund/
├── strategies/               # Strategy logic (mean reversion, momentum, factor)
├── backtesting/              # Backtesting engine and helpers
├── portfolio/                # Construction, risk, and allocation logic
├── reporting/                # HTML + PDF report generation
├── dashboard/                # Streamlit dashboard app
├── data/                     # Raw and processed historical data
├── notebooks/                # Research and exploration notebooks
├── docs/                     # Final outputs (reports, notes)
├── main.py                   # Entrypoint script
```

---

## Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/ArmaanG06/ASG-Microfund.git
cd asg-microfund
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/Scripts/activate  # or venv\bin\activate on mac
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the main simulation:**

```bash
python main.py
```

5. **Launch the dashboard:**

```bash
streamlit run dashboard/streamlit_app.py
```

---

## Milestone Roadmap

| Week | Focus Area               | Outcome                                         |
| ---- | ------------------------ | ----------------------------------------------- |
| 1    | Setup + Mean Reversion   | Backtest engine and first strategy working      |
| 2    | Momentum + Factor Stratgies'|  strategy construction and finalization      |
| 3    |  Portfolio               | portfolio construction                          |
| 4    | Reporting + Streamlit    | PDF & HTML reports + dashboard MVP              |
| 5    | Publishing + Cleanup     | documentation + full repo ready + README        |

---

## Documentation & Deliverables

* `/docs/` – Reports, research notes, demo links
* `/notebooks/` – Exploratory research and strategy tuning
* `/README.md` – You’re here
* `/generate_report.py` – Generates automated monthly reports
* `/streamlit_app.py` – Live dashboard interface

---

## Future Enhancements

* Add machine learning signal generation
* Integrate macroeconomic overlays
* Deploy dashboard to Streamlit Cloud
* Add paper trading API (Alpaca or Interactive Brokers)
* Build real-time investor portal + strategy scheduler
* Convert to ASG Microfund 2.0 and use real capital to trade with

---

## ✉️ Contact

Built by Armaan Gandhara as a hybrid quant portfolio and personal development project. For questions or collaboration inquiries, email: [agandhara243@gmail.com](mailto:agandhara243@gmail.com) or connect on [LinkedIn](https://www.linkedin.com/in/armaan-gandhara/)



**License**: MIT 

**Date**: 07/05/2025 
