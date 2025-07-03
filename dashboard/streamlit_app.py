import streamlit as st
import pandas as pd
from datetime import datetime as date

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from portfolio.construction import Portfolio

# -- Streamlit UI Setup --

st.set_page_config(page_title='ASG Microfund Dashboard', layout='wide')
st.title("ASG Microfund Preformance Dashboard")

# -- Sidebar: User Inputs --
st.sidebar.header("Simulation Configuration")

start_date = st.sidebar.date_input("Start Date", date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", date(2025, 1, 1))

commissions = st.sidebar.slider("Commissions (%)", 0.0, 10.0, 0.1, 0.01)
cash = st.sidebar.number_input("Starting Cash ($)", min_value=1000, max_value=1_000_000, value=100_000, step=1000)

mean_tickers = st.sidebar.text_area("Mean Reversion Tickers (comma-separated)", "AAPL,MSFT,GOOGL")
factor_tickers = st.sidebar.text_area("Factor Investing Tickers (comma-separated)", "BRK-B,JNJ,UNH")
mean_ticker_list = [t.strip().upper() for t in mean_tickers.split(",") if t.strip()]
factor_ticker_list = [t.strip().upper() for t in factor_tickers.split(",") if t.strip()]

run_simulation = st.sidebar.button("Run Portfolio Backtest")

if run_simulation:
    with st.spinner("Running portfolio backtest..."):
        try:
            port = Portfolio(
                start=start_date,
                end=end_date,
                commissions=commissions,
                cash=cash,
                mean_tickers=mean_ticker_list,
                factor_tickers=factor_ticker_list
            )

            mean_results, mom_results, factor_results, final_metrics, benchmark_metrics = port.backtest_portfolio()

            st.success("Backtest complete!")

            # Display Metrics
            st.header("Final Portfolio Metrics")
            st.dataframe(pd.DataFrame(final_metrics, index=["Metrics"]))

            st.header("Strategy Summaries")
            st.subheader("Mean Reversion")
            st.dataframe(pd.DataFrame(mean_results).T)

            st.subheader("Momentum")
            st.dataframe(pd.DataFrame(mom_results).T)

            st.subheader("Factor Investing")
            st.dataframe(pd.DataFrame(factor_results).T)

        except Exception as e:
            st.error(f"Error during simulation: {e}")
            
        else:
            st.info("Configure inputs in the sidebar and click 'Run Portfolio Backtest' to begin.")


