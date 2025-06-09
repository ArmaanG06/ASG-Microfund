import yfinance as yf
import pandas as pd
from typing import List, Union


class data_loader:

    def __init__(self):
        pass

    def get_data(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        ticker = ticker.replace('.', '-')

        data = yf.download(ticker, start=start, end=end, progress=False)
        if data.empty:
            print(f"[!] Failed to download {ticker}. Skipping.")
            return None
        data.dropna(inplace=True)
        if 'Adj Close' in data.columns:
            data.drop(columns=['Adj Close'], inplace=True)
        #data.rename(columns={'Open': 'open','High': 'high','Low': 'low','Close': 'close','Volume': 'volume'}, inplace=True)
        #required_cols = ['open', 'high', 'low', 'close', 'volume']
        #data = data[required_cols]
        data = data.droplevel('Ticker', axis=1)
        data.reset_index(inplace=True)
        data.index = data['Date']
        del data['Date']
        data.index.name = 'Date'

        return data


    def get_multiple_data(self, tickers: List[str], start: str, end: str) -> dict:
        data_dict = {}
        for ticker in tickers:
            df = self.get_data(ticker, start, end)
            if df is not None:
                data_dict[ticker] = df

        return data_dict
    
    def get_sp500_data(self, start: str, end: str):
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        sp500 = sp500['Symbol'].to_list()
        data = self.get_multiple_data(sp500, start, end)
        return data
