from datetime import datetime, timedelta
from helpers.logger import get_logger

def clearup(api, order_list, config):
    # orders
    n_cleared = 0
    for id, symbol in order_list:
        try:
            api.cancel_order(id, symbol)
            n_cleared += 1
        except:
            pass

    # positions
    n_candles = config['general']['n_future_candles']
    timenow  = datetime.now()
    max_diff = timedelta(minutes=15*n_candles)
    profit_threshold = config['general']['tp'] * config['general']['position_size'] * (1/3) 
    for position in api.get_positions_full():
        if float(position['unrealisedPnl']) > profit_threshold and timenow - datetime.fromtimestamp(float(position['createdTime']) // 1000) > max_diff:
            api.close_position(position['symbol'], 'Sell' if position['side'] == 'Buy' else 'Buy', position['size'])
    return n_cleared 


logger = get_logger()
def print_stats(api, list_orders, n_current, n_cleared):
    logger.info(f"completed loop, statisitcs:")

    """ commenting now because it does not work

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
    """
    logger.info(f'ntrades: {len(list_orders)}')
    logger.info(f'balance: {api.get_balance()}')
    logger.info(api.get_positions())

def divide(a, b):
    try:
        return a / b
    except:
        return 0
    
def filtered_symbols(api, config):
    """
    def fil(s):
        price = api.klines(s, limit=2).Close[-1]
        return price > config['general']['symbol_llimit'] and price < config['general']['symbol_hlimit']
    symbols = api.get_symbols(config['general']['n_tickers'])
    return list(filter(fil, symbols))
    """
    lst = ['10000WENUSDT', '1000FLOKIUSDT', '1000LUNCUSDT', '1000RATSUSDT', '1000TURBOUSDT', '1000XECUSDT', '1INCHUSDT', 'ACEUSDT', 'ADAUSDT', 'AERGOUSDT', 'AEVOUSDT', 'AGIUSDT', 'AGIXUSDT', 'AGLDUSDT', 'AIUSDT', 'ALGOUSDT', 'ALICEUSDT', 'ALPACAUSDT', 'ALPHAUSDT', 'ALTUSDT', 'ANKRUSDT', 'ANTUSDT', 'APEUSDT', 'API3USDT', 'APTUSDT', 'ARBUSDT', 'ARKMUSDT', 'ARKUSDT', 'ARPAUSDT', 'ARUSDT', 'ASTRUSDT', 'ATAUSDT', 'ATOMUSDT', 'AUCTIONUSDT', 'AUDIOUSDT', 'AVAXUSDT', 'AXLUSDT', 'AXSUSDT', 'BADGERUSDT', 'BAKEUSDT', 'BALUSDT', 'BANDUSDT', 'BATUSDT', 'BELUSDT', 'BICOUSDT', 'BIGTIMEUSDT', 'BLURUSDT', 'BLZUSDT', 'BNTUSDT', 'BNXUSDT', 'BOBAUSDT', 'BONDUSDT', 'BSVUSDT', 'BSWUSDT', 'C98USDT', 'CAKEUSDT', 'CEEKUSDT', 'CELOUSDT', 'CETUSUSDT', 'CFXUSDT', 'CHRUSDT', 'CHZUSDT', 'COMBOUSDT', 'COMPUSDT', 'COREUSDT', 'COTIUSDT', 'CROUSDT', 'CRVUSDT', 'CTCUSDT', 'CTKUSDT', 'CTSIUSDT', 'CVCUSDT', 'CVXUSDT', 'CYBERUSDT', 'DAOUSDT', 'DARUSDT', 'DASHUSDT', 'DATAUSDT', 'DODOUSDT', 'DOGEUSDT', 'DOTUSDT', 'DUSKUSDT', 'DYDXUSDT', 'DYMUSDT', 'EDUUSDT', 'EGLDUSDT', 'ENAUSDT', 'ENJUSDT', 'ENSUSDT', 'EOSUSDT', 'ETCUSDT', 'ETHFIUSDT', 'ETHWUSDT', 'FETUSDT', 'FILUSDT', 'FLMUSDT', 'FLOWUSDT', 'FORTHUSDT', 'FRONTUSDT', 'FTMUSDT', 'FXSUSDT', 'GALAUSDT', 'GALUSDT', 'GASUSDT', 'GLMRUSDT', 'GLMUSDT', 'GMTUSDT', 'GMXUSDT', 'GODSUSDT', 'GPTUSDT', 'GRTUSDT', 'GTCUSDT', 'HBARUSDT', 'HFTUSDT', 'HIFIUSDT', 'HIGHUSDT', 'HNTUSDT', 'HOOKUSDT', 'ICPUSDT', 'ICXUSDT', 'IDEXUSDT', 'IDUSDT', 'IMXUSDT', 'INJUSDT', 'IOTAUSDT', 'IOTXUSDT', 'JOEUSDT', 'JTOUSDT', 'JUPUSDT', 'KASUSDT', 'KAVAUSDT', 'KDAUSDT', 'KLAYUSDT', 'KNCUSDT', 'KSMUSDT', 'LDOUSDT', 'LINKUSDT', 'LITUSDT', 'LOOKSUSDT', 'LOOMUSDT', 'LPTUSDT', 'LQTYUSDT', 'LRCUSDT', 'LSKUSDT', 'LTOUSDT', 'LUNA2USDT', 'MAGICUSDT', 'MANAUSDT', 'MANTAUSDT', 'MASKUSDT', 'MATICUSDT', 'MAVIAUSDT', 'MAVUSDT', 'MBOXUSDT', 'MDTUSDT', 'METISUSDT', 'MINAUSDT', 'MNTUSDT', 'MOVRUSDT', 'MTLUSDT', 'MYROUSDT', 'NEARUSDT', 'NEOUSDT', 'NFPUSDT', 'NKNUSDT', 'NMRUSDT', 'NTRNUSDT', 'OCEANUSDT', 'OGNUSDT', 'OGUSDT', 'OMGUSDT', 'OMUSDT', 'ONDOUSDT', 'ONGUSDT', 'ONTUSDT', 'OPUSDT', 'ORCAUSDT', 'ORDIUSDT', 'ORNUSDT', 'OXTUSDT', 'PENDLEUSDT', 'PERPUSDT', 'PHBUSDT', 'PIXELUSDT', 'POLYXUSDT', 'POPCATUSDT', 'PORTALUSDT', 'POWRUSDT', 'PROMUSDT', 'PYTHUSDT', 'QTUMUSDT', 'RADUSDT', 'RAREUSDT', 'RDNTUSDT', 'RENUSDT', 'REQUSDT', 'RIFUSDT', 'RLCUSDT', 'RNDRUSDT', 'RONUSDT', 'ROSEUSDT', 'RPLUSDT', 'RSS3USDT', 'RUNEUSDT', 'SANDUSDT', 'SCAUSDT', 'SCRTUSDT', 'SEIUSDT', 'SFPUSDT', 'SKLUSDT', 'SLERFUSDT', 'SNXUSDT', 'SSVUSDT', 'STEEMUSDT', 'STGUSDT', 'STORJUSDT', 'STPTUSDT', 'STRKUSDT', 'STXUSDT', 'SUIUSDT', 'SUPERUSDT', 'SUSHIUSDT', 'SXPUSDT', 'THETAUSDT', 'TIAUSDT', 'TOKENUSDT', 'TOMIUSDT', 'TONUSDT', 'TRBUSDT', 'TRUUSDT', 'TRXUSDT', 'TWTUSDT', 'UMAUSDT', 'UNFIUSDT', 'UNIUSDT', 'VANRYUSDT', 'VGXUSDT', 'WAVESUSDT', 'WAXPUSDT', 'WIFUSDT', 'WLDUSDT', 'WOOUSDT', 'WUSDT', 'XAIUSDT', 'XLMUSDT', 'XNOUSDT', 'XRDUSDT', 'XRPUSDT', 'XTZUSDT']
    return lst[:config['general']['n_tickers']]