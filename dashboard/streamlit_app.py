import streamlit as st
import pandas as pd
from datetime import datetime as date
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from portfolio.construction import Portfolio

# -- Streamlit UI Setup --

st.set_page_config(page_title='ASG Microfund Dashboard', layout='wide')
st.title("ASG Microfund Preformance Dashboard")

# -- Sidebar: User Inputs --
st.sidebar.header("Simulation Configuration")

start_date = st.sidebar.text_input("Start Date", '2020-01-01')
end_date = st.sidebar.text_input("End Date", '2025-01-01')

risk_tol = st.sidebar.text_input("Risk Tolerance","medium")
time_hor = st.sidebar.text_input("Time Horizon","medium")

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
                commissions=(commissions/100),
                cash=cash,
                mean_tickers=mean_ticker_list,
                factor_tickers=factor_ticker_list,
                user_tolerance=risk_tol,
                user_time=time_hor
            )

            mean_results, mom_results, factor_results, final_metrics, benchmark_metrics = port.backtest_portfolio()


            benchmark_metrics_sum = {}
            keys = ['Return [%]', 'CAGR [%]', 'Max. Drawdown [%]']
            for key in keys:
                benchmark_metrics_sum[key] = benchmark_metrics[key]

            st.success("Backtest complete!")

            # Display Metrics

            st.header("Final Portfolio Metrics")
            st.dataframe(pd.DataFrame(final_metrics, index=["Metrics"]))

            st.header("Benchmark Comparison")
            st.dataframe(benchmark_metrics_sum)

            st.header("Strategy Summaries")
            st.subheader("Mean Reversion")
            st.dataframe(pd.DataFrame(mean_results).T)

            st.subheader("Momentum")
            st.dataframe(mom_results)

            st.subheader("Factor Investing")
            st.dataframe(factor_results)

            st.link_button("Download Full Report", "https://www.youtube.com/")
            #st.download_button("Download Report", )

        except Exception as e:
            st.error(f"Error during simulation: {e}")

        
            
else:
    st.info("Configure inputs in the sidebar and click 'Run Portfolio Backtest' to begin.")


