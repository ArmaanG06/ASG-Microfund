from reporting.generate_report import generate_report, generate_pdf
import pandas as pd

start_date = '2020-01-01'
end_date = '2025-01-01'
user_risk_tol = 'medium'
user_time_hor = 'medium'
mean_tickers = ['CL=F']
tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]['Symbol'].tolist()
factor_tickers = [t.replace('.', '-') for t in tickers]
commissions = 0.001
cash = 1000000


generate_report(start_date, end_date, user_risk_tol, user_time_hor, mean_tickers, factor_tickers, commissions, cash)


#----------- IN PROGRESS ------------
#generate_pdf(start_date, end_date, user_risk_tol, user_time_hor) 

#----------- TO RUN STREAMLIT DASHBOARD -----------

# streamlit run dashboard/streamlit_app.py
