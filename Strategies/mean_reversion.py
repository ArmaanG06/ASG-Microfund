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
    bb_length = 20
    bb_std = 2.0
    rsi_length = 14
    rsi_lower = 30
    rsi_upper = 70
    atr_length = 14
    position_size = 0.2  # 20% of equity per trade
    
    def init(self):
        # Calculate indicators once during initialization
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # Bollinger Bands with error handling
        bb = ta.bbands(close, length=self.bb_length, std=self.bb_std)
        if bb is not None:
            self.lower_band = self.I(lambda x: bb[f'BBL_{self.bb_length}_{self.bb_std}'].values, 'Lower Band')
            self.upper_band = self.I(lambda x: bb[f'BBU_{self.bb_length}_{self.bb_std}'].values, 'Upper Band')
        else:
            # Fallback if BB calculation fails
            self.lower_band = self.I(lambda x: np.full(len(x), np.nan), 'Lower Band')
            self.upper_band = self.I(lambda x: np.full(len(x), np.nan), 'Upper Band')
        
        # RSI with error handling
        rsi = ta.rsi(close, length=self.rsi_length)
        self.rsi = self.I(lambda x: rsi.values if rsi is not None else np.full(len(x), np.nan), 'RSI')
        
        # ATR with error handling
        atr = ta.atr(high, low, close, length=self.atr_length)
        self.atr = self.I(lambda x: atr.values if atr is not None else np.full(len(x), np.nan), 'ATR')
        
        # Volume filter with error handling
        volume_sma = ta.sma(pd.Series(self.data.Volume), length=20)
        self.volume_filter = self.I(lambda x: volume_sma.values if volume_sma is not None else np.zeros(len(x)), 'Volume Filter')

    def next(self):
        # Skip if indicators aren't ready
        if (np.isnan(self.rsi[-1]) or 
            np.isnan(self.lower_band[-1]) or 
            np.isnan(self.atr[-1])):
            return
            
        # Current values
        price = self.data.Close[-1]
        atr = self.atr[-1] if not np.isnan(self.atr[-1]) else 0
        
        # Only trade when volume is above average
        if self.data.Volume[-1] < self.volume_filter[-1]:
            return
            
        # Entry conditions
        if not self.position:
            # Long entry (oversold condition)
            if price < self.lower_band[-1] and self.rsi[-1] < self.rsi_lower:
                stop_loss = price - 1.5 * atr
                take_profit = price + 3 * atr
                self.buy(size=self.position_size, sl=stop_loss, tp=take_profit)
                
            # Short entry (overbought condition)
            elif price > self.upper_band[-1] and self.rsi[-1] > self.rsi_upper:
                stop_loss = price + 1.5 * atr
                take_profit = price - 3 * atr
                self.sell(size=self.position_size, sl=stop_loss, tp=take_profit)
        
        # Dynamic exit for long positions
        elif self.position.is_long and (price > self.upper_band[-1] or self.rsi[-1] > 60):
            self.position.close()
            
        # Dynamic exit for short positions
        elif self.position.is_short and (price < self.lower_band[-1] or self.rsi[-1] < 40):
            self.position.close()
