import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



class factor_investing_screener:

    def __init__(self, data_loader, tickers):
        self.loader = data_loader
        self.tickers = tickers
        self.passed = []

    def _get_features(self):
        for ticker in self.tickers:
            info = self.loader.get_fundamentals(ticker)
            # Check all required keys exist
            required_keys = [
                'priceToBook', 'trailingPE', 'forwardPE', 'enterpriseToEbitda',
                'debtToEquity', 'returnOnEquity', 'returnOnAssets', 'grossMargins',
                'operatingMargins', 'freeCashflow', 'revenueGrowth', 'earningsGrowth',
                'beta', 'marketCap'
            ]

            missing_keys = [k for k in required_keys if k not in info or info[k] is None]
            if missing_keys:
                print(f"[!] Skipping {ticker} — missing keys: {missing_keys}")
                continue


            if all(k in info and info[k] is not None for k in required_keys):
                self.passed.append({
                    'ticker': ticker,
                    'p_b': info['priceToBook'],
                    'pe_ttm': info['trailingPE'],
                    'pe_forward': info['forwardPE'],
                    'ev_ebitda': info['enterpriseToEbitda'],
                    'debt_to_equity': info['debtToEquity'],
                    'roe': info['returnOnEquity'],
                    'roa': info['returnOnAssets'],
                    'gross_margin': info['grossMargins'],
                    'operating_margin': info['operatingMargins'],
                    'fcf': info['freeCashflow'],
                    'revenue_growth': info['revenueGrowth'],
                    'earnings_growth': info['earningsGrowth'],
                    'beta': info['beta'],
                    'market_cap': info['marketCap']
                })
            time.sleep(0.2)  # avoid hitting API rate limits
        return self.passed 
    
    def choose_stocks(self, top_n=10):
        self._get_features()
        df = pd.DataFrame(self.passed)

        if df.empty:
            raise ValueError("No data available to screen.")

        # Invert value metrics: lower is better
        df['p_b_rank'] = df['p_b'].rank(ascending=True)
        df['pe_ttm_rank'] = df['pe_ttm'].rank(ascending=True)
        df['pe_forward_rank'] = df['pe_forward'].rank(ascending=True)
        df['ev_ebitda_rank'] = df['ev_ebitda'].rank(ascending=True)

        # Quality metrics: higher is better
        df['roe_rank'] = df['roe'].rank(ascending=False)
        df['roa_rank'] = df['roa'].rank(ascending=False)
        df['gross_margin_rank'] = df['gross_margin'].rank(ascending=False)
        df['operating_margin_rank'] = df['operating_margin'].rank(ascending=False)

        # Growth metrics: higher is better
        df['revenue_growth_rank'] = df['revenue_growth'].rank(ascending=False)
        df['earnings_growth_rank'] = df['earnings_growth'].rank(ascending=False)

        # Combine all ranks into a composite score (equal weighting for now)
        df['composite_score'] = df[
            [
                'p_b_rank', 'pe_ttm_rank', 'pe_forward_rank', 'ev_ebitda_rank',
                'roe_rank', 'roa_rank', 'gross_margin_rank', 'operating_margin_rank',
                'revenue_growth_rank', 'earnings_growth_rank'
            ]
        ].mean(axis=1)

        df_sorted = df.sort_values(by='composite_score')
        top_stocks = df_sorted.head(top_n).reset_index(drop=True)

        return top_stocks
            

class factor_investing_strategy():

    def __init__(self, start_date, end_date, commission, data_loader, tickers):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.commission = commission / 100
        self.screener = factor_investing_screener(data_loader, tickers)
        self.loader = data_loader
        self.portfolio = []
        self.returns = []

    def get_stocks(self, date):
        top_stocks = self.screener.choose_stocks()
        return top_stocks['ticker'].tolist()
    
    def backtest(self):
        rebalance_dates = pd.date_range(self.start_date, self.end_date, freq='12M')

        # Track portfolio cumulative return
        cum_pf = []

        # Loop through each period
        for i in range(len(rebalance_dates) - 1):
            rebalance_date = rebalance_dates[i]
            next_rebalance = rebalance_dates[i + 1]

            # Get tickers to hold
            tickers = self.get_stocks(rebalance_date)
            if not tickers:
                print(f"[!] No stocks selected for {rebalance_date.date()}. Skipping.")
                continue

            # Download price data for period
            data_dict = self.loader.get_multiple_data(tickers, start=rebalance_date, end=next_rebalance)
            prices = pd.DataFrame({ticker: df['Close'] for ticker, df in data_dict.items() if 'Close' in df})

            if prices.empty:
                print(f"[!] No valid price data for {rebalance_date.date()}. Skipping.")
                continue

            prices = prices.dropna(axis=1, how='any')  # drop any stocks with missing prices
            if prices.shape[1] == 0:
                continue

            # Calculate equal-weighted returns
            rets = prices.pct_change().dropna()
            pf_ret = rets.mean(axis=1) * (1 - self.commission)
            cum_pf.append(pf_ret)

        if not cum_pf:
            print("[!] No portfolio returns were calculated.")
            return None

        # Combine and calculate cumulative performance
        pf_series = pd.concat(cum_pf)
        pf_cum = (1 + pf_series).cumprod()

        self.returns = pf_series
        self.portfolio = pf_cum

        return pf_cum

    def plot_performance(self):
        if self.portfolio is None or self.portfolio.empty:
            print("[!] No portfolio performance to plot.")
            return

        plt.figure(figsize=(12, 6))
        plt.plot(self.portfolio, label='Factor Investing Strategy')
        plt.title('Factor Investing Strategy Performance')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def get_metrics(self, risk_free_rate=0.02):
        returns = self.returns
        if returns is None or returns.empty:
            return None

        ann_ret = (1 + returns.mean()) ** 12 - 1
        ann_vol = returns.std() * np.sqrt(12)
        sharpe = (ann_ret - risk_free_rate) / ann_vol if ann_vol != 0 else np.nan
        cum_returns = self.portfolio
        drawdown = cum_returns / cum_returns.cummax() - 1
        max_dd = drawdown.min()

        metrics = {
            'Return [%]': returns.iloc[-1],
            'CAGR [%]': ann_ret,
            'Sharpe Ratio': sharpe,
            'Max. Drawdown [%]': max_dd
        }

        return metrics
    


