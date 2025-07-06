import time
import key_file

from eth_account.signers.local import LocalAccount
import eth_account 
import json
import time
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import ccxt
import pandas as pd
import datetime
import schedule
import requests

symbol = 'SOL'
timeframe = '4h'
size = 10 # in USD


def ask_bid(symbol):
    '''this gets the ask and bid for any symbol passed in'''
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    data = {
        'type': 'l2Book',
        'coin': symbol
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    l2_data = response.json()
    l2_data = l2_data['levels']

    # get the ask and bid from the l2_data
    ask = float(l2_data[1][0]['px'])
    bid = float(l2_data[0][0]['px'])

    return ask, bid, l2_data

def get_sz_px_decimals(coin):
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'meta'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        data = response.json()
        symbols = data['universe']
        symbol_info = next((s for s in symbols if s['name'] == coin), None)
        if symbol_info:
            sz_decimals = symbol_info['szDecimals']
        else:
            print('symbol not found')
            return None, None
    else:
        print(f'Error: {response.status_code}')
        return None, None
    
    ask, bid, _ = ask_bid(coin)
    ask_str = str(ask)
    if '.' in ask_str:
        px_decimals = len(ask_str.split('.')[1])
    else:
        px_decimals = 0

    print(f'{coin} this is the price {sz_decimals} decimals')
    return sz_decimals, px_decimals

# Make a buy and a sell order
def limit_order(coin, is_buy, sz, limit_px, reduce_only, account):
    exchange = Exchange(account, constants.MAINNET_API_URL)
    rounding = get_sz_px_decimals(coin)[0]
    if rounding is not None:
        sz = round(sz, rounding)
    print(f'coin: {coin}, type: {type(coin)}')
    print(f'is_buy: {is_buy}, type: {type(is_buy)}')
    print(f'reduce_only: {reduce_only}, type: {type(reduce_only)}')
    print(f'sz: {sz}, type: {type(sz)}')

    print(f'placing limit order for {coin} {sz} @ {limit_px}')
    order_result = exchange.order(coin, is_buy, sz, limit_px, {"limit": {"tif": 'Gtc'}}, reduce_only=reduce_only)
    if is_buy == True:
        print(f'limit BUY order placed thanks neo, resting: {order_result["response"]["data"]["statuses"][0]}')
    else:
        print(f'limit SELL order placed thanks neo, resting: {order_result["response"]["data"]["statuses"][0]}')

    return order_result

# Main execution

coin = symbol
is_buy = True
ask, bid, l2 = ask_bid(coin)
reduce_only = False
secret_key = key_file.private_key
account = LocalAccount = eth_account.Account.from_key(secret_key)

    # Buy order
limit_order(coin, is_buy, size, bid, reduce_only, account)
time.sleep(5)

# Sell order
is_buy = False
reduce_only = True
limit_order(coin, is_buy, size, ask, reduce_only, account)

time.sleep(5)    






