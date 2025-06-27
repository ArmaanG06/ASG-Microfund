from backtesting import Strategy
import pandas as pd
import pandas_ta as ta
import numpy as np

class mean_reversion_strategy_custom():
    def __init__(self, lookback: int = 20, std_dev: float = 2.0, threshold: float = 0.0):
        """
        Mean Reversion strategy using Bollinger Bands.
        
        :param lookback: Rolling window size for Bollinger Bands (e.g., 20 periods).
        :param std_dev: Number of standard deviations for Bollinger Bands (e.g., 2.0).
        :param threshold: Optional buffer percentage away from band before triggering signal (e.g., 0.0 for no buffer).

        This version is not used since it does not inherit the strategy class from backtesting.py library and therefore
        cannot run through the backtesting and output the detailed graphs and metrics
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
    # Strategy parameters
    bb_length = 20
    bb_std = 2.0
    rsi_length = 15
    rsi_lower = 30
    rsi_upper = 70
    atr_length = 14
    
    def init(self):        
        price = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)

        bb = ta.bbands(close=price, length=self.bb_length, std=self.bb_std)
        rsi = ta.rsi(price, self.rsi_length)
        atr = ta.atr(high, low, price, self.atr_length)
        volume_sma = ta.sma(pd.Series(self.data.Volume), length=20)
        

        self.lower = self.I(lambda x: bb[f'BBL_{self.bb_length}_{self.bb_std}'], 'BB_Lower')
        self.upper = self.I(lambda x: bb[f'BBU_{self.bb_length}_{self.bb_std}'], 'BB_Upper')
        self.middle = self.I(lambda x: bb[f'BBM_{self.bb_length}_{self.bb_std}'], 'BB_Middle')
        self.rsi = self.I(lambda x: rsi, 'RSI')
        self.atr = self.I(lambda x: atr.values, 'ATR')
        self.volume_sma = self.I(lambda x: volume_sma.values, 'Volume Filter')

    def next(self):
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        upper = self.upper[-1]
        lower = self.lower[-1]
        rsi = self.rsi[-1]
        atr = self.atr[-1]
        volume_sma = self.volume_sma[-1]
        #print(self.data.index)            
        
        
        if volume < volume_sma:
            return

        if not self.position:
            if price < lower and rsi < self.rsi_lower:
                sl = price - 1.5 * atr
                tp = price + 3.0 * atr
                self.buy(size=0.5)

            elif price> upper and rsi > self.rsi_upper:
                sl = price + 1.5 * atr
                tp = price - 3.0 * atr 
                self.sell(size=0.5, sl=sl, tp=tp)

        #if self.position.is_long


        elif self.position.is_long and price > upper:
            self.position.close()

        elif self.position.is_short and price < lower:
            self.position.close()
