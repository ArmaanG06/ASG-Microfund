import yfinance as yf
import os
import pandas as pd
from typing import List, Union
import json


class data_loader:

    def __init__(self):
        self.raw_path = "./data/raw"
        self.processed_path = "./data/processed"

    def _raw_filepath(self, ticker: str) -> str:
        return os.path.join(self.raw_path, f"{ticker}.csv")

    def get_data(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        ticker = ticker.replace('.', '-')

        filepath = self._raw_filepath(ticker)

        if os.path.exists(filepath):
            data = pd.read_csv(filepath, index_col='Date', parse_dates=True)
            sliced_data = data.loc[start:end]
            print(f"Retrieving {ticker} data from csv")
            if not sliced_data.empty:
                return sliced_data

        print(f"Downloading {ticker} from yfinance...")
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
        data.to_csv(filepath)
        return data.loc[start:end]


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

    def get_sp500_data_df(self, start: str, end: str) -> pd.DataFrame:
        tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]['Symbol'].tolist()
        tickers = [t.replace('.', '-') for t in tickers]
        data_dict = self.get_multiple_data(tickers, start, end)
        close_prices = [df[['Close']].rename(columns={'Close': ticker}) for ticker, df in data_dict.items()]
        return pd.concat(close_prices, axis=1) if close_prices else pd.DataFrame()
    
    def get_fundamentals(self, ticker):
        ticker = ticker.replace('.', '-')
        file_path = os.path.join(self.raw_path, f"{ticker}_fundamentals.json")

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    fundamentals = json.load(f)
                print(f"[!] Loading fundamentals from file for {ticker}")
                return fundamentals
            except Exception as e:
                print(f"[!] Failed to load fundamentals from file for {ticker}: {e}")

        try:
            print(f"[i] Downloading fundamentals for {ticker} from Yahoo Finance... ")
            fundamentals = yf.Ticker(ticker).info
            with open(file_path, 'w') as f:
                json.dump(fundamentals, f)
            return fundamentals
        except Exception as e:
            print(f"[!] Failed to download fundamentals for {ticker}: {e}")
            return {}
