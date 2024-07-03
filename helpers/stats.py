from helpers.logger import get_logger

logger = get_logger()

def print_stats(api, list_orders, n_current, n_cleared):
    logger.info(f"completed loop, statisitcs:")
    pnl_list = api.get_pl()
    order_list = api.get_orders()
    filtered_orders = list(filter(lambda x: x["orderId"] in list_orders, order_list))

    def filtering(x):
        for order in filtered_orders:
            if order['symbol'] == x['symbol'] and order['side'] != x['side'] and order['qty'] == x['qty']:
                return True
        return False
    filtered_pnl = list(filter(filtering, pnl_list))

    final_pl = 0
    n_trades = len(list_orders)
    wins = [] 
    loses = [] 
    for closed in filtered_pnl:
        floated_pnl = float(closed['closedPnl'])
        final_pl += floated_pnl
        if floated_pnl >= 0:
            wins.append(floated_pnl)
        else:
            loses.append(floated_pnl)
    
    logger.info(f"CURRENT PnL: {final_pl} ;  average_profit: {divide(sum(wins), len(wins))} ;  average_loss: {divide(sum(loses), len(loses))}  ;   n_trades: {n_trades}  ; won+lost: {len(wins) + len(loses)} ; winrate: {divide(len(wins), len(wins) + len(loses))} ; currently_open: {n_current} ; n_cleared: {n_cleared}")
    logger.info(f'balance: {api.get_balance()}')
    logger.info(api.get_positions())
    logger.info("----------------------")

def divide(a, b):
    try:
        return a / b
    except:
        return 0