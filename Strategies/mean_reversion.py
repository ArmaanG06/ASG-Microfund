from backtesting import Strategy
import pandas as pd
import pandas_ta as ta

class mean_reversion_strategy_custom():
    def __init__(self, lookback: int = 20, std_dev: float = 2.0, threshold: float = 0.0):
        """
        Mean Reversion strategy using Bollinger Bands.
        
        :param lookback: Rolling window size for Bollinger Bands (e.g., 20 periods).
        :param std_dev: Number of standard deviations for Bollinger Bands (e.g., 2.0).
        :param threshold: Optional buffer percentage away from band before triggering signal (e.g., 0.0 for no buffer).
        """
        self.lookback = lookback
        self.std_dev = std_dev
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell/hold signals based on Bollinger Bands mean reversion logic
        
        :param data: OHLCV DataFrame (must include 'close' column, not 'adj close')
        :return: Dataframe with 'signal' column where 1 = buy, -1 = sell, 0 = hold
        """
        df = data.copy()
        bb = ta.bbands(close=df['close'], length=self.lookback, std=self.std_dev)
        if bb is None or bb.empty:
            raise ValueError("Bollinger Bands calculation failed. Check input data.")
        df = df.join(bb)
        df['signal'] = 0  # Default to hold (0)
        # Buy signal: price below lower band (with optional threshold buffer)
        df.loc[df['close'] < df[f'BBL_{self.lookback}_{self.std_dev}'] * (1 - self.threshold), 'signal'] = 1
        # Sell signal: price above upper band (with optional threshold buffer)
        df.loc[df['close'] > df[f'BBU_{self.lookback}_{self.std_dev}'] * (1 + self.threshold), 'signal'] = -1
        return df[['signal']]
    



class mean_reversion_strategy(Strategy):
    def init(self):
        # Pre-compute Bollinger Bands once at strategy initialization
        price = pd.Series(self.data.Close)
        bb = ta.bbands(close=price, length=20, std=2.0)

        # Store indicators
        self.lower = self.I(lambda: bb[f'BBL_20_2.0'])
        self.upper = self.I(lambda: bb[f'BBU_20_2.0'])

    def next(self):
        price = self.data.Close[-1]
        # Entry logic
        if price < self.lower[-1] and not self.position:
            self.buy()
        elif price > self.upper[-1] and not self.position:
            self.sell()

        # Exit logic
        if self.position.is_long and price > self.data.Close[-2]:
            self.position.close()
        elif self.position.is_short and price < self.data.Close[-2]:
            self.position.close()
