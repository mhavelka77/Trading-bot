import multiprocessing
import os
while not os.path.isfile('config.yaml'):
    os.chdir("../")

import yaml
from helpers.helpers import filtered_symbols
from datetime import timedelta, datetime

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

from api.api import Api
api = Api.create_api(config)
from backtest.strategies import create_features_b, create_features_d

data_window = api.klines("BTCUSDT", limit=200)
features_b = create_features_b(data_window).keys()
features_d = create_features_d(data_window).keys()

sl = 0.008
tp = 0.04

def get_signal(last_index, data, direction):
    upper_good = data.Close[last_index] * (1 + tp)
    lower_good = data.Close[last_index] * (1 - tp)
    upper_bad = data.Close[last_index] * (1 + sl)
    lower_bad = data.Close[last_index] * (1 - sl)

    crossed_low = False
    crossed_high = False

    for i in range(1, 10):
        if data.High[last_index + i] > upper_bad:
            crossed_high = True
            if crossed_low:
                return 0
        if data.Low[last_index + i] < lower_bad:
            crossed_low = True
            if crossed_high:
                return 0

        if data.High[last_index + i] > upper_good and not crossed_low:
            return 1
        if data.Low[last_index + i] < lower_good and not crossed_high:
            if direction:
                return -1
            else:
                return 1 
    return 0

def data_from_symbol(symbol_ar):
    nwindows = 750
    window_size = 200
    timenow = datetime.now()

    limit = 1000
    try:
        if symbol_ar[1]:
            endtime = int((timenow - timedelta(minutes=15 * 1000 * 1)).timestamp() * 1000)
            klines = api.end_timed_klines(symbol_ar[0], endtime, '15', limit=limit)
        else:
            endtime = int((timenow - timedelta(minutes=15 * 1000 * 2)).timestamp() * 1000)
            klines = api.end_timed_klines(symbol_ar[0], endtime, '15', limit=limit)

    except:
        return []

    if len(klines) < 999:
        return []
    symbol_rows = []
    for i in range(nwindows):
        data_window = klines[i:i+window_size]
        new_row = create_features_d(data_window) if symbol_ar[2] else create_features_b(data_window)
        signal = get_signal(i+window_size-1, klines, symbol_ar[2])
        new_row['target'] = signal
        symbol_rows.append(new_row)
    return symbol_rows


def driver_func(test=False, direction=False):
    symbols = filtered_symbols(api, config) 
    symbols = [[s, test, direction] for s in symbols]
    PROCESSES = 10
    with multiprocessing.Pool(PROCESSES) as pool:
        results = pool.map_async(data_from_symbol, symbols)
        results = results.get()
    return results