import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from pybit.unified_trading import HTTP
import pandas as pd
import pickle
import os.path


class Bybit():
    @staticmethod
    def create_session(config):
        if config['general']['testnet']:
            return HTTP(
                api_key=config['api_keys']['bybit']['test']['api_key'],
                api_secret=config['api_keys']['bybit']['test']['api_secret'],
                testnet=True
            )
        else:
            return HTTP(
                api_key=config['api_keys']['bybit']['prod']['api_key'],
                api_secret=config['api_keys']['bybit']['prod']['api_secret'],
                testnet=False
            )
    def __init__(self, config):
        self.config = config
        self.session = Bybit.create_session(config)
        if os.path.isfile('./api/static/store'):
            with open('./api/static/store', 'rb') as f:
                self.store = pickle.load(f)

    def get_balance(self):
        return float(self.session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalEquity'])

    def get_symbols(self, n):
        resp = self.session.get_tickers(category='linear')['result']['list']
        return [elem['symbol'] for elem in resp if 'USDT' in elem['symbol'] and not 'USDC' in elem['symbol']][:n]

    def klines(self, symbol, timeframe='15', limit=1000):
        private_session = Bybit.create_session(self.config) 
        resp = private_session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=limit + 1
        )['result']['list']

        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        resp = resp.set_index("Time")
        resp = resp.astype(float)
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp[::-1]
        resp = resp.iloc[:-1]
        return resp
 
    def static_klines(self, symbol):
        return self.store[symbol] 

    def get_old_price(self, symbol):
        return self.klines(symbol, limit=5).Close[-1]

    def start_timed_klines(self, symbol, start_time, timeframe='1', limit=15):
        private_session = Bybit.create_session(self.config) 
        resp = private_session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=limit,
            start=start_time
        )['result']['list']

        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'] 
        resp = resp.set_index("Time")
        resp = resp.astype(float)
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp[::-1]
        return resp
    
    def end_timed_klines(self, symbol, end_time, timeframe='15', limit=1000):
        private_session = Bybit.create_session(self.config) 
        resp = private_session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=limit,
            end=end_time
        )['result']['list']

        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'] 
        resp = resp.set_index("Time")
        resp = resp.astype(float)
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp[::-1]
        return resp

    def get_positions(self):
        resp =  self.session.get_positions(
            category="linear",
            settleCoin="USDT",
            limit=200
        )['result']['list']
        return [elem['symbol'] for elem in resp]
    
    def get_positions_full(self):
        return self.session.get_positions(
            category="linear",
            settleCoin="USDT",
            limit=200
        )['result']['list']

    def set_mode(self, symbol, leverage):
        try:
            resp = self.session.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=leverage,
                sellLeverage=leverage
            )
            return resp
        except:
            return

    def get_precisions(self, symbol):
        resp = self.session.get_instruments_info(
            category='linear',
            symbol=symbol    
        )['result']['list'][0]
        price = resp['priceFilter']['tickSize']
        if '.' in price:
            price = len(price.split('.')[1])
        else:
            price = 0
        qty = resp['lotSizeFilter']['qtyStep']
        if '.' in qty:
            qty = len(qty.split('.')[1])
        else:
            qty = 0
        
        return price, qty

    def place_order_market(self, symbol, side, tp, sl, compensation, qty):
        price_precision, qty_precision = self.get_precisions(symbol)
        old_price = self.get_old_price(symbol)
        old_price = old_price * (1 + compensation) if side == 'buy' else old_price * (1 - compensation)
        order_qty = round(qty / old_price, qty_precision)

        tp_price = round(old_price * (1 + tp) if side == 'buy' else old_price * (1 - tp), price_precision)
        sl_price = round(old_price * (1 - sl) if side == 'buy' else old_price * (1 + sl), price_precision)
        old_price = round(old_price, price_precision)
        return self.session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == 'buy' else 'Sell',
            orderType='Limit',
            price=old_price,
            qty=order_qty,
            takeProfit=tp_price,
            stopLoss=sl_price
        )

    def close_position(self, symbol, side, qty):
        return self.session.place_order(
            category='linear',
            symbol=symbol,
            side=side,
            orderType='Market',
            qty=qty,
            time_in_force="GoodTillCancel",
            reduceOnly=True,
            close_on_trigger=False,
        )

    def get_pl(self):
        res = self.session.get_closed_pnl(
            category='linear',
            limit=200,
        )
        result = res['result']['list']
        while res['result']['nextPageCursor']:
            res = self.session.get_closed_pnl(
                category='linear',
                cursor=res['result']['nextPageCursor'],
                limit=200,
            )
            result += res['result']['list']
        return result

    def get_orders(self):
        res = self.session.get_order_history(
            category='linear',
        )
        result = res['result']['list']
        currentn = 0
        while res['result']['nextPageCursor'] and currentn < 200:
            currentn += 1
            res = self.session.get_order_history(
                category='linear',
                cursor=res['result']['nextPageCursor'],
            )
            result += res['result']['list']
        return result
    
    def get_open_orders(self):
        res = self.session.get_open_orders(
            category='linear',
            settleCoin='USDT',
            orderFilter='Order',
        )
        result = res['result']['list']
        currentn = 0
        while res['result']['nextPageCursor'] and currentn < 200:
            currentn += 1
            res = self.session.get_open_orders(
                category='linear',
                settleCoin='USDT',
                orderFilter='Order',
                cursor=res['result']['nextPageCursor'],
            )
            result += res['result']['list']
        return result

    def cancel_order(self, id, symbol):
        res = self.session.cancel_order(
            category='linear',
            orderId=id,
            symbol=symbol,
        )
        return res


    def get_order_book(self, symbol):
        return self.session.get_orderbook(
            category="linear",
            symbol=symbol,
        )