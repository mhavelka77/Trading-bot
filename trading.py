import time
from datetime import datetime
import multiprocessing as mp
import yaml

import backtest.strategies as strategies
from helpers.helpers import print_stats, clearup, filtered_symbols
from helpers.logger import get_logger
from api.api import Api

logger = get_logger()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

strategy = getattr(strategies, config['general']['strategy_function']) 
api = Api.create_api(config)

def worker_task(symbol):
    data = api.klines(symbol, config['general']['timeframe'], limit=config['general']['datapoints'])
    signal = strategy(data)
    return symbol, signal

if __name__ == '__main__':
    symbols = filtered_symbols(api, config) 
    logger.info(f"nsymbols: {len(symbols)}")
    logger.info(f"initial balance: {api.get_balance()}")

    if config['general']['state']:
        with open("./state", 'r') as f:
            orders = f.readlines()
        orders = [s.strip() for s in orders]
        logger.info(f"loaded {len(orders)} past orders")
    else:
        orders = []

    n_cleared = 0
    current_orders = []
    while True:
        assert api.get_balance() > config['general']['balance_limit'], f"hit the balance limit of {config['general']['balance_limit']}, exitting..."
        
        while (datetime.now().minute not in [0, 15, 30, 45]):
            time.sleep(1)
        logger.info("----------------------")
        n_pos = len(api.get_positions())
        if n_pos > config['general']['max_pos']:
            logger.info(f"balance: {api.get_balance()}")
            time.sleep(60)
            continue

        positions = api.get_positions()
        logger.info("Generating signals...")
        free_symbols = list(filter(lambda x: x not in positions, symbols))

        with mp.Pool(processes=config['general']['n_processes']) as pool: 
            results = pool.map(worker_task, free_symbols)

        logger.info("Ordering signaled symbols...")
        for symbol, signal in results:
            if signal == 0:
                continue
            if n_pos > config['general']['max_pos']:
                break
            api.set_mode(symbol, config['general']['leverage'])
            try:
                order_id = api.place_order_market(symbol, 'buy' if signal == 1 else 'sell', config['general']['tp'], config['general']['sl'], config['general']['compensation'], config['general']['position_size'])['result']['orderId']
                if order_id:
                    orders.append(order_id)
                    current_orders.append((order_id, symbol))
                    n_pos += 1
            except Exception as e:
                logger.error(f'error when placing order: {e}')

        print_stats(api, orders, len(api.get_positions()), n_cleared)
        time.sleep(70)
        logger.info("running cleanup")
        cleared = clearup(api, current_orders, config)
        logger.info(f"cleaned {cleared} orders")
        logger.info("----------------------")
        n_cleared += cleared 
        current_orders = []

        with open("./state", 'w') as f:
            for order in orders:
                f.write(f"{order}\n")