import pandas as pd
import numpy as np
import ta
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator
from ta.volume import OnBalanceVolumeIndicator

# Constants
INPUT_FILE = "premarket_smallcaps.csv"
OUTPUT_FILE = "premarket_smallcaps_with_signals.csv"

def calculate_signal(df):
    # Calculate Bollinger Bands
    bb_indicator = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb_indicator.bollinger_hband()
    df['bb_lower'] = bb_indicator.bollinger_lband()
    
    # Calculate RSI
    rsi_indicator = RSIIndicator(close=df['close'], window=14)
    df['rsi'] = rsi_indicator.rsi()
    
    # Calculate Moving Averages
    short_ema = EMAIndicator(close=df['close'], window=12)
    long_ema = EMAIndicator(close=df['close'], window=26)
    df['short_ema'] = short_ema.ema_indicator()
    df['long_ema'] = long_ema.ema_indicator()
    
    # Calculate MACD
    macd_indicator = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['macd'] = macd_indicator.macd()
    df['macd_signal'] = macd_indicator.macd_signal()
    
    # Calculate Stochastic Oscillator
    stoch_indicator = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
    df['%K'] = stoch_indicator.stoch_k()
    df['%D'] = stoch_indicator.stoch_d()
    
    # Calculate VWAP
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    # Calculate Parabolic SAR
    df['sar'] = ta.trend.stc(high=df['high'], low=df['low'], close=df['close'], window_slow=50, window_fast=13)
    
    # Calculate OBV
    obv_indicator = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume'])
    df['obv'] = obv_indicator.on_balance_volume()
    
    # Initialize signals
    df['signal'] = 0
    
    # Bollinger Bands signal
    df.loc[df['close'] > df['bb_upper'], 'signal'] += 1
    df.loc[df['close'] < df['bb_lower'], 'signal'] -= 1
    
    # RSI signal
    df.loc[df['rsi'] > 70, 'signal'] -= 1
    df.loc[df['rsi'] < 30, 'signal'] += 1
    
    # EMA signal
    df.loc[df['short_ema'] > df['long_ema'], 'signal'] += 1
    df.loc[df['short_ema'] < df['long_ema'], 'signal'] -= 1
    
    # MACD signal
    df.loc[df['macd'] > df['macd_signal'], 'signal'] += 1
    df.loc[df['macd'] < df['macd_signal'], 'signal'] -= 1
    
    # Stochastic Oscillator signal
    df.loc[(df['%K'] > df['%D']) & (df['%K'] < 20), 'signal'] += 1
    df.loc[(df['%K'] < df['%D']) & (df['%K'] > 80), 'signal'] -= 1
    
    # VWAP signal
    df.loc[df['close'] > df['vwap'], 'signal'] += 1
    df.loc[df['close'] < df['vwap'], 'signal'] -= 1
    
    # Parabolic SAR signal
    df.loc[df['sar'] < df['close'], 'signal'] += 1
    df.loc[df['sar'] > df['close'], 'signal'] -= 1
    
    # OBV signal
    df['obv_diff'] = df['obv'].diff()
    df.loc[df['obv_diff'] > 0, 'signal'] += 1
    df.loc[df['obv_diff'] < 0, 'signal'] -= 1
    
    # Clamp signal
    df['signal'] = df['signal'].clip(-3, 3)
    
    return df

def main():
    # Read the premarket data
    df = pd.read_csv(INPUT_FILE)
    # Calculate the signals
    df = calculate_signal(df)
    # Save the dataframe with the new signal column
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()
