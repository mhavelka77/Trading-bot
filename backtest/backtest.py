STATS_FOLDER = './statistics/'
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from hashlib import md5
import inspect
from os.path import exists
from tqdm import tqdm
import istarmap as istarmap 
from multiprocessing import Pool
import yaml
from datetime import datetime, timedelta

with open('./config.yaml', 'r') as f:
    config = yaml.safe_load(f)

from helpers.helpers import filtered_symbols
from api.api import Api
api = Api.create_api(config)

def goes_up(symbol, data, index, upper_limit, lower_limit, side):
    price_precision,_ = api.get_precisions(symbol)
    upper_limit = round(upper_limit, price_precision)
    lower_limit = round(lower_limit, price_precision)
    n_candles = config['general']['n_future_candles']

    for i in range(index, index + n_candles):
        if data.High[i] >= upper_limit and data.Low[i] > lower_limit:
            return 1
        if data.Low[i] <= lower_limit and data.High[i] < upper_limit:
            return -1
        if data.High[i] >= upper_limit and data.Low[i] <= lower_limit:
            start_time = int(data.index[i].timestamp() * 1000)
            finer_data = api.start_timed_klines(symbol=symbol, start_time=start_time)
            for n in range(15):
                if finer_data.High[n] >= upper_limit and finer_data.Low[n] > lower_limit:
                    return 1
                if finer_data.Low[n] <= lower_limit and finer_data.High[n] < upper_limit:
                    return -1
                if side == 1:
                    if finer_data.Low[n] <= lower_limit:
                        return 0
                if side == -1:
                    if finer_data.High[n] >= upper_limit:
                        return 0
            return 0
        if side == 1:
            if data.Low[i] <= lower_limit:
                return 0
        if side == -1:
            if data.High[i] >= upper_limit:
                return 0
    return 0


def backtest(data, predictor, sl, tp, window_size, symbol):
    compensation = config['general']['compensation']
    nwindows = len(data) - window_size
    n_candles = config['general']['n_future_candles']
    success = 0 
    fail = 0 
    for i in range(nwindows - n_candles):
        data_window = data.iloc[i:i + window_size]
        prediction = predictor(data_window)
        if prediction == 1:
            if 1 == goes_up(symbol, data, i + window_size, data.Close[i + window_size - 1] * (1 + compensation) * (1 + tp), data.Close[i + window_size - 1] * (1 + compensation) * (1 - sl), 1):
                success += 1
            else:
                fail += 1
        elif prediction == -1: 
            if -1 == goes_up(symbol, data, i + window_size, data.Close[i + window_size - 1] * (1 - compensation) * (1 + sl), data.Close[i + window_size - 1] * (1 - compensation) * (1 - tp), -1):
                success += 1
            else:
                fail += 1
    return (nwindows, success, fail) 

def worker_task(symbol, timeframe, limit, predictor, sl, tp, window_size, history):
    if history:
        timenow = datetime.now()
        endtime = int((timenow - timedelta(minutes=int(timeframe) * limit * 2)).timestamp() * 1000)
        data = api.end_timed_klines(symbol, endtime, timeframe, limit)
    else:
        data = api.klines(symbol, timeframe, limit)
    return backtest(data, predictor, sl, tp, window_size, symbol)


def combined_backtest(predictor, sl=0.01, tp=0.01, timeframe='15', save=True, window_size=200, limit=1000, n_processes=15, history=False):
    symbols = filtered_symbols(api, config)
    symbols = [(symbol, timeframe, limit, predictor, sl, tp, window_size, history) for symbol in symbols]
    with Pool(processes=n_processes) as pool: 
        results = list(tqdm(pool.istarmap(worker_task, symbols), total=len(symbols)))
    
    nwindows = 0
    success = 0
    fails = 0
    for result in results:
        nwindows += result[0] 
        success += result[1] 
        fails += result[2] 

    trade_rate = (success + fails) / nwindows
    win_rate = success / (success + fails)

    summary = f"The indicator {predictor.__name__} was tested on {nwindows} scenarios. n_trades = {success + fails}      Trade-rate = {trade_rate}      Win-rate = {win_rate}"
    print(summary)
    
    if save:
        function_code = inspect.getsource(predictor)
        function_hash = md5(function_code.encode()).hexdigest()

        file_path = f"{STATS_FOLDER}{function_hash}"     
        if not exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"{function_code} \n---\n")
        with open(file_path, "a") as f:
            f.write(f"{sl};{tp};{nwindows};{success+fails};{trade_rate};{win_rate}\n")
