import warnings

import ta.momentum
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

# test functions
import random
def random_dummy(data):
    return random.choice([-1, 1])

def hold_dummy(data):
    return 0 

def sell_dummy(data):
    return -1 

def buy_dummy(data):
    return 1 

# RSI function
import ta
def rsi_20(data):
    rsi = ta.momentum.RSIIndicator(data.Close).rsi()
    if rsi.iloc[-2] < 20 and rsi.iloc[-1] > 20:
      return 1 
    if rsi.iloc[-2] > 80 and rsi.iloc[-1] < 80:
      return -1 
    return 0 

def rsi_25(data):
    rsi = ta.momentum.RSIIndicator(data.Close).rsi()
    if rsi.iloc[-2] < 25 and rsi.iloc[-1] > 25:
      return 1 
    if rsi.iloc[-2] > 75 and rsi.iloc[-1] < 75:
      return -1 
    return 0 

def rsi_30(data):
    rsi = ta.momentum.RSIIndicator(data.Close).rsi()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
      return 1 
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
      return -1 
    return 0 

# simple indicator (gemini generated)
def adx_signal(data):
  adx = ta.trend.ADXIndicator(data.High, data.Low, data.Close).adx()
  pos_di = ta.trend.ADXIndicator(data.High, data.Low, data.Close).adx_pos()
  neg_di = ta.trend.ADXIndicator(data.High, data.Low, data.Close).adx_neg()

  if len(adx) < 3:
    return 0
  if pos_di.iloc[-1] > neg_di.iloc[-1] and pos_di.iloc[-2] < neg_di.iloc[-2]:
    return 1
  elif pos_di.iloc[-1] < neg_di.iloc[-1] and pos_di.iloc[-2] > neg_di.iloc[-2]:
    return -1
  else:
    return 0
  
# MACD function (gemini generated)
def macd_signal(data):
  macd = ta.trend.MACD(data.Close)
  macd_line = macd.macd()
  signal_line = macd.macd_signal()
  if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
    return 1
  if macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
    return -1
  return 0


# Stochastic RSI (gemini) 
def stochastic_rsi_signal(data):
  stoch_rsi = ta.momentum.StochRSIIndicator(data.Close).stochrsi()
  latest_stoch_rsi = stoch_rsi.iloc[-2:]
  if latest_stoch_rsi.iloc[0] < 0.2 and latest_stoch_rsi.iloc[1] > 0.2:
    return 1
  if latest_stoch_rsi.iloc[0] > 0.8 and latest_stoch_rsi.iloc[1] < 0.8:
    return -1
  return 0

# Moving Average Crossover function (gemini)
def moving_average_crossover_signal(data, short_window=20, long_window=50):
  short_ma = data.Close.rolling(window=short_window).mean()
  long_ma = data.Close.rolling(window=long_window).mean()
  latest_short_ma = short_ma.iloc[-2:]
  latest_long_ma = long_ma.iloc[-2:]
  if latest_short_ma.iloc[0] < latest_long_ma.iloc[0] and latest_short_ma.iloc[1] > latest_long_ma.iloc[1]:
    return 1
  if latest_short_ma.iloc[0] > latest_long_ma.iloc[0] and latest_short_ma.iloc[1] < latest_long_ma.iloc[1]:
    return -1
  return 0

def bollinger_width(prices):
  bbands = ta.volatility.BollingerBands(prices.Close).bollinger_wband()
  bbands /= bbands.std()
  return bbands[-1] < 1

def candle_height(prices):
  heights = prices.High - prices.Low
  heights /= heights.std()
  return heights[-1] > 1

def bollinger_bands_signal(data):
  bollinger_bands = ta.volatility.BollingerBands(data.Close)
  upper_band = bollinger_bands.bollinger_hband()
  lower_band = bollinger_bands.bollinger_lband()

  if data.High[-1] > upper_band.iloc[-1] and data.Close[-1] <= data.Close[0]:
    return -1
  elif data.Low[-1] < lower_band.iloc[-1] and data.Close[-1] >= data.Close[0]:
    return 1
  return 0

# https://www.youtube.com/watch?v=mYNqikThZvQ&t=378s  
def youtube1(data):
  ema = ta.trend.EMAIndicator(data.Close, window=100).ema_indicator()
  rsi = ta.momentum.RSIIndicator(data.Close).rsi()
  if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30 and data.Close[-1] < ema[-1]:
      return 1 
  if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70 and data.Close[-1] > ema[-1]:
      return -1 
  else:
      return 0  


# two EMAs crossing + some RSI
def ema_crossing(data):
  ema1= ta.trend.EMAIndicator(data.Close, window=5).ema_indicator()
  ema2= ta.trend.EMAIndicator(data.Close, window=20).ema_indicator()
  rsi = ta.momentum.RSIIndicator(data.Close).rsi()

  if rsi.iloc[-2] < 40 and rsi.iloc[-1] > 40 and ema1[-2] < ema2[-2] and ema1[-1] > ema2[-1]:
      return 1 
  if rsi.iloc[-2] > 60 and rsi.iloc[-1] < 60 and ema1[-2] > ema2[-2] and ema1[-1] < ema2[-1]:
      return -1 
  else:
      return 0  
  
# stcindicator https://howtotrade.com/blog/best-scalping-indicators/ + rsi
def stc_indicator(data):
  stc = ta.trend.STCIndicator(data.Close).stc()
  rsi = ta.momentum.RSIIndicator(data.Close).rsi()
  if rsi.iloc[-2] > 65 and rsi.iloc[-1] < 65 and stc[-2] >= 70 and stc[-1] < 70:
     return -1
  if rsi.iloc[-2] < 35 and rsi.iloc[-1] > 35 and stc[-2] <= 30 and stc[-1] > 30:
     return 1
  return 0

import numpy as np
    
def combined_1(prices):
  in1 = stochastic_rsi_signal(prices)
  in2 = rsi_30(prices)

  if in1 == 1 and in2 == 1:
    return 1
  if in1 == -1 and in2 == -1:
    return -1
  return 0

def combined_2(prices):
  in1 = stochastic_rsi_signal(prices)
  in2 = rsi_30(prices)
  in3 = macd_signal(prices)

  if in1 == 1 and in2 == 1 and in3 == 1:
    return 1
  if in1 == -1 and in2 == -1 and in3 == -1:
    return -1
  return 0




def chat_gpt_2(prices):
       # Calculate various indicators
    sma_short = ta.trend.sma_indicator(prices.Close, window=20)  # 20-period Simple Moving Average
    sma_long = ta.trend.sma_indicator(prices.Close, window=50)   # 50-period Simple Moving Average
    macd = ta.trend.MACD(prices.Close).macd_diff()               # MACD
    bbands = ta.volatility.BollingerBands(prices.Close).bollinger_hband()          # Bollinger Bands
    atr = ta.volatility.average_true_range(prices.High, prices.Low, prices.Close)  # Average True Range

    # Entry conditions
    entry_condition = (
        (prices.Close > sma_short) &                 # Price above short-term SMA
        (prices.Close > sma_long) &                  # Price above long-term SMA
        (macd > 0) &                    # MACD histogram positive
        (prices.Close < bbands) &       # Price below lower Bollinger Band
        (atr.iloc[-1] > atr.mean())                  # ATR above its mean
    )

    # Exit conditions
    exit_condition = (
        (prices.Close < sma_short) |                 # Price below short-term SMA
        (prices.Close < sma_long) |                  # Price below long-term SMA
        (macd < 0) |                    # MACD histogram negative
        (prices.Close > bbands) |       # Price above upper Bollinger Band
        (atr.iloc[-1] < atr.mean())                  # ATR below its mean
    )

    if entry_condition.iloc[-1]:
        return 1  # Buy signal
    elif exit_condition.iloc[-1]:
        return -1  # Sell signal
    else:
        return 0  # No signal
    
def gpt4_3(prices):
    short_sma = ta.trend.SMAIndicator(prices.Close, window=20).sma_indicator()
    long_sma = ta.trend.SMAIndicator(prices.Close, window=50).sma_indicator()
    if short_sma.iloc[-2] < long_sma.iloc[-2] and short_sma.iloc[-1] > long_sma.iloc[-1]:
        return 1
    elif short_sma.iloc[-2] > long_sma.iloc[-2] and short_sma.iloc[-1] < long_sma.iloc[-1]:
        return -1
    else:
        return 0
    
def combined_3(prices):
  in1 = combined_1(prices)
  in2 = gpt4_3(prices)

  if in1 == 1 and in2 == 1:
    return 1
  if in1 == -1 and in2 == -1:
    return -1
  return 0


from ta.trend import MACD
from ta.volatility import BollingerBands

# Indicator function
def gpt4_4(prices):
    # RSI logic
    rsi = ta.momentum.RSIIndicator(prices.Close).rsi()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        rsi_signal = 1 
    elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        rsi_signal = -1 
    else:
        rsi_signal = 0 

    # MACD logic
    macd_indicator = MACD(prices.Close)
    macd_line = macd_indicator.macd()
    signal_line = macd_indicator.macd_signal()
    if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
        macd_signal = 1
    elif macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
        macd_signal = -1
    else:
        macd_signal = 0

    # Bollinger Bands logic
    upper_band = BollingerBands(prices.Close).bollinger_hband_indicator()
    lower_band = BollingerBands(prices.Close).bollinger_lband_indicator()
    if lower_band.iloc[-2] > prices.Close.iloc[-2] and lower_band.iloc[-1] < prices.Close.iloc[-1]:
        band_signal = 1
    elif upper_band.iloc[-2] < prices.Close.iloc[-2] and upper_band.iloc[-1] > prices.Close.iloc[-1]:
        band_signal = -1
    else:
        band_signal = 0

    # Voting system
    signal_sum = rsi_signal + macd_signal + band_signal
    if signal_sum > 0:
        return 1
    elif signal_sum < 0:
        return -1
    else:
        return 0
    

def combined_4(prices):
  in1 = combined_1(prices)
  in2 = gpt4_4(prices)

  if in1 == 1 and in2 == 1:
    return 1
  if in1 == -1 and in2 == -1:
    return -1
  return 0


def combined_5(prices):
  in1 = rsi_30(prices)
  in2 = gpt4_4(prices)

  if in1 == 1 and in2 == 1:
    return 1
  if in1 == -1 and in2 == -1:
    return -1
  return 0

def gpt4_5(prices):
    signals = []

    # RSI Calculation 
    rsi = ta.momentum.RSIIndicator(prices['Close']).rsi()

    # RSI Signal
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        signals.append(1)
    elif rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        signals.append(-1)

    # MACD Calculation 
    macd = ta.trend.MACD(prices['Close']).macd()

    # MACD Signal
    if macd.iloc[-2] <= 0 and macd.iloc[-1] > 0:
        signals.append(1)
    elif macd.iloc[-2] >=0 and macd.iloc[-1] < 0:
        signals.append(-1)

    # Bollinger Bands Calculation 
    BB = ta.volatility.BollingerBands(prices['Close'])

    # Bollinger Signal
    if prices['Close'].iloc[-1] <= BB.bollinger_lband().iloc[-1]:
        signals.append(1)
    elif prices['Close'].iloc[-1] >= BB.bollinger_hband().iloc[-1]:
        signals.append(-1)

    # Stochastic Oscillator Calculation 
    sto = ta.momentum.StochasticOscillator(prices['High'], prices['Low'], prices['Close'])

    # Stochastic Signal
    if sto.stoch_signal().iloc[-1] > 80:
        signals.append(-1)
    elif sto.stoch_signal().iloc[-1] < 20:
        signals.append(1)

    # Voting system to determine the final signal 
    signal_count = sum(signals)

    if signal_count >=2:
        return 1 
    elif signal_count <= -3:
        return -1 
    else:
        return 0
    
def martin_1(prices):
  ema50 = ta.trend.EMAIndicator(prices.Close, window=50).ema_indicator()
  ema100 = ta.trend.EMAIndicator(prices.Close, window=100).ema_indicator()
  stoch = ta.momentum.StochasticOscillator(prices.High, prices.Low, prices.Close).stoch()

  if ema50.iloc[-1] > ema100.iloc[-1] and stoch.iloc[-1] > 20 and stoch.iloc[-2] < 20 and prices.Close.iloc[-1] < ema50.iloc[-1]:
    return 1
  if ema50.iloc[-1] < ema100.iloc[-1] and stoch.iloc[-1] < 80 and stoch.iloc[-2] > 80 and prices.Close.iloc[-1] > ema50.iloc[-1]:
    return -1
  return 0

def chat_gpt_3(prices):
    rsi = ta.momentum.RSIIndicator(prices.Close).rsi()
    macd = ta.trend.macd_diff(prices.Close)
    bbands = ta.volatility.BollingerBands(prices.Close)
    atr = ta.volatility.AverageTrueRange(prices.High, prices.Low, prices.Close).average_true_range()
    
    if rsi.iloc[-1] > 70 and macd.iloc[-1] > 0 and prices.Close.iloc[-1] > bbands.bollinger_hband().iloc[-1]:
        return -1
    elif rsi.iloc[-1] < 30 and macd.iloc[-1] < 0 and prices.Close.iloc[-1] < bbands.bollinger_lband().iloc[-1]:
        return 1
    elif rsi.iloc[-1] > 70 and atr.iloc[-1] > atr.mean() * 2:
        return -1
    elif rsi.iloc[-1] < 30 and atr.iloc[-1] > atr.mean() * 2:
        return 1
    else:
        return 0
    
def martin_2(prices):
  ema50 = ta.trend.EMAIndicator(prices.Close, window=50).ema_indicator()
  ema20 = ta.trend.EMAIndicator(prices.Close, window=20).ema_indicator()
  stoch = ta.momentum.StochasticOscillator(prices.High, prices.Low, prices.Close).stoch()

  if ema20.iloc[-1] > ema50.iloc[-1] and stoch.iloc[-1] > 20 and stoch.iloc[-2] < 20 and prices.Close.iloc[-1] < ema20.iloc[-1]:
    return 1
  if ema20.iloc[-1] < ema50.iloc[-1] and stoch.iloc[-1] < 80 and stoch.iloc[-2] > 80 and prices.Close.iloc[-1] > ema20.iloc[-1]:
    return -1
  return 0


def trend(prices):
  return prices.Close.iloc[-1] > prices.Open.iloc[-1]


def gpt4_6(prices):
  macd = ta.trend.MACD(prices.Close)
  sma_short = ta.trend.SMAIndicator(prices.Close, window=12)
  sma_long = ta.trend.SMAIndicator(prices.Close, window=26)
  
  buy_signal = ((macd.macd_diff() > 0) & (sma_short.sma_indicator() > sma_long.sma_indicator()))
  sell_signal = ((macd.macd_diff() < 0) & (sma_short.sma_indicator() < sma_long.sma_indicator()))
  
  if buy_signal.iloc[-1] and not buy_signal.iloc[-2]:
      return 1
  elif sell_signal.iloc[-1] and not sell_signal.iloc[-2]:
      return -1
  else:
      return 0
  
def gpt4_7(prices):
  macd = ta.trend.MACD(prices.Close)
  bb_High = ta.volatility.BollingerBands(prices.Close, window=20).bollinger_hband()
  bb_low = ta.volatility.BollingerBands(prices.Close, window=20).bollinger_lband()

  condition1 = (macd.macd_diff() > 0) & (prices.Close.iloc[-1] < bb_low.iloc[-1])
  condition2 = (macd.macd_diff() < 0) & (prices.Close.iloc[-1] > bb_High.iloc[-1])

  if condition1.all() and not condition1.shift(-1).iloc[-2]:
      return 1
  elif condition2.all() and not condition2.shift(-1).iloc[-2]:
      return -1
  else:
      return 0


def martin_3(prices):
  if prices.Close[-1] > prices.Close[0]:
    if ta.volatility.BollingerBands(prices.Close).bollinger_lband_indicator()[-1]:
      return 1
  else:
    if ta.volatility.BollingerBands(prices.Close).bollinger_hband_indicator()[-1]:
      return -1
  return 0

def combined_13(prices):
  others = [moving_average_crossover_signal(prices), ema_above(prices), ema_crossing(prices)]
  martin = martin_3(prices)
  if martin == 1 and 1 in others:
     return 1 
  elif martin == -1 and -1 in others:
     return -1
  return 0


def bull_candle(prices):
  return 1 if prices.Close[-1] > prices.Open[-1] else -1

def ema_above(prices):
  ema = ta.trend.EMAIndicator(prices.Close).ema_indicator()
  return 1 if prices.Close[-1] < ema[-1] else -1

def bull_and_ema(prices):
   bull = bull_candle(prices)
   ema = ema_above(prices)

   if bull == 1 and ema == 1:
      return 1
   if bull == -1 and ema == -1:
      return -1
   return 0

####### ML
#######
def create_features_b(prices):
  indicators = [
    ta.momentum.PercentageVolumeOscillator(prices.Volume).pvo_signal(),
    ta.volatility.AverageTrueRange(prices.High, prices.Low, prices.Close).average_true_range() / ta.volatility.AverageTrueRange(prices.High, prices.Low, prices.Close).average_true_range().std()
  ]
  result = {}
  hist = 4 
  for n in range(len(indicators)):
    for i in range(1, hist):
     result[f'{n}_{i}'] = indicators[n][-i] 
  return result

def create_features_d(prices):
  indicators = [
    ta.momentum.PercentagePriceOscillator(prices.Close).ppo_signal(),
    ta.momentum.StochasticOscillator(prices.High, prices.Low, prices.Close).stoch_signal(),
    ta.momentum.RSIIndicator(prices.Close).rsi(), 
  ]

  result = {}
  hist = 3
  for n in range(len(indicators)):
    for i in range(1, hist):
     result[f'{n}_{i}'] = indicators[n][-i] 
  return result


import numpy as np
from xgboost import XGBClassifier
breakout_model = XGBClassifier()
breakout_model.load_model('./ml/breakout_model.json')

direction_model = XGBClassifier()
direction_model.load_model('./ml/direction_model.json')

def ml_breakout(prices):
  features = create_features_b(prices)
  model_input = np.array(list(features.values())).reshape(1, -1)
  return breakout_model.predict(model_input)

def ml_direction(prices):
  features = create_features_d(prices)
  model_input = np.array(list(features.values())).reshape(1, -1)
  return direction_model.predict(model_input)

def ml_strategy(prices):
  if ml_breakout(prices):
     return ml_direction(prices)
  return 0

######
######
import os
from datetime import datetime
while not os.path.isfile('config.yaml'):
    os.chdir("../")
import yaml
with open('./config.yaml', 'r') as f:
    config = yaml.safe_load(f)

from api.api import Api
api = Api.create_api(config)

from datetime import timedelta

btcprices = api.klines('BTCUSDT')
def btc_follower(prices):
  btc = btcprices[(btcprices.index - timedelta(minutes=4)) < prices.index[-1]]
  base = btc.Close[-6]
  if btc.Close[-1] < base * 0.98:
    return -1
  if btc.Close[-1] > base * 1.02:
    return 1
  return 0

def martin_4(prices):
  rsi = ta.momentum.RSIIndicator(prices.Close).rsi()
  bollinger_bands = ta.volatility.BollingerBands(prices.Close)
  upper_band = bollinger_bands.bollinger_hband()
  lower_band = bollinger_bands.bollinger_lband()

  if prices.Low[-1] < lower_band[-1] * 0.998 and rsi[-2] == rsi[-5:].min():
     return 1
  if prices.High[-1] > upper_band[-1] * 1.002 and rsi[-2] == rsi[-5:].max():
     return -1
  return 0

