#### Coding Risk Management ###

import ccxt
import key_file as k
import time, schedule
import pandas as pd

bitget = ccxt.bitget({
    'enableRateLimit': True,
    'apiKey': k.key,
    'secret': k.secret,
})

bal = bitget.fetch_balance()

symbol = 'uBTCUSD'
size = 1
bid = 29000
params = {'timeInForce': 'PostOnly'}

# open positions.
def open_positions(symbol=symbol):
# what is the pooisition index for that symbol?
    if symbol == 'uBTCSUSD':
        index_pos = 4

        # other symbols, symbol indexes are different on other exchanges

    params = {'type':'swap', 'code':'USD'}
    phe_bal = bitget.fetch_balance(params=params)
    open_positions = phe_bal[info]['data']['positions']
        #print(open_positions)
    openpos_side = open_positions[index_pos]['side'] 
    openpos_size = open_positions[index_pos][size]
        #print(open_positions)

    if openpos_side == ('BUY'):
        openpos_bool = True
        long = True
    elif openpos_side == ('Sell'):
        openpos_bool = True
        long = False
    else:
        openpos_bool = False
        long = None
    print(f'open_positions... | openpos_bool {openpos_bool} | openpos_size {openpos_size} | long {long} | index_pos {index_pos}')

    return(open_positions, openpos_bool, openpos_size, long, index_pos)


# ask_bid
def ask_bid(symbol=symbol):
    ob = bitget.fetch_order_book(symbol)

    bid = ob['bids'][0][0]
    ask = ob['asks'][0][0]
# f literal
    print(f'this is the ask for {symbol} {ask}')
    return ask, bid # ask_bid()[0] = ask, [1] = bid 

# kill switch - when called exits position - guardrails for liquidity
def kill_switch(symbol=symbol):

    print(f'starting the kill switch for{symbol}')
    openposi = open_positions(symbol[1])
    long = open_positions(symbol[3])
    kill_size = open_positions(symbol[2])

    print(f'openposi {openposi}, long{long}, size{kill_size}')

    while openposi == True:
        print('starting kill switch loop until limit is full')
        temp_df = pd.DataFrame()
        print('just made a temporary df')

        bitget.cancel_all_orders(symbol)
        openposi = open_positions(symbol)[1]
        long = open_positions(symbol[3])
        kill_size = open_positions(symbol)[2]
        kill_size = int(kill_size)

        ask = ask_bid(symbol)[0] 
        bid = ask_bid(symbol)[1] 

        if long == False:
            bitget.create_limit_buy_order(symbol, kill_size, bid, ask)
            print(f'just made a BUY to CLOSE order of {kill_size}')
            print('sleeping for 30 seconds to see if it fills...')
            time.sleep(30)
        if long == True:
            bitget.create_limit_sell_order(symbol, kill_size, ask, params)
            print(f'just made a SELL to CLOSE order of {kill_size} {symbol}')
            print('sleeping for 30 seconds to see if it fills...')
        else:
            print('++++++ SOMETHING I DIDNT EXPECT IN THE KILLSWITCH HAPPENED')

target = 9
max_loss = -8

# pnl close
def pnl_close(symbol=symbol, target=target, max_loss=max_loss):
    print(f'checking to see if its time to exit for {symbol}... ')

    params = {'type':"swap", 'code':'USD'}
    pos_dict = bitget.fetch_positions(params=params)
    #print(pos_dict)

    index_pos = open_positions(symbol)[4]
    pos_dict = pos_dict[index_pos]
    side = pos_dict['side']
    size = pos_dict['contracts']
    entry_price = float(pos_dict['entryPrice'])
    leverage = float(pos_dict['leverage'])

    current_price = ask_bid(symbol)[1]

    print(f'side :{side} | entry_price: {entry_price} | lev: {leverage}')

    if side == 'long':
        diff = current_price - entry_price
        long = True
    else:
        diff = entry_price - current_price
        long = False
    try:
        perc = round(((diff/entry_price) * leverage), 10)
    except:
        perc = 0
    
    perc = 100*perc
    print(f'foe {symbol} this is our PNL percentage: {(perc)}%')

    pnlclose = False
    in_pos = False

    if perc > 0:
        in_pos = True
        print(f'for {symbol} we are in a winning position')
        if perc > target:
            print(':):) we are in profit & hit target...checking')
            pnlclose = True
            kill_switch(symbol)
        else:
            print('we have not hit our target yet')
    elif perc > 0:
        in_pos = True
        if perc <= max_loss:
            print(f'we need to exit now down {perc}... so starting the kill switch')
            kill_switch(symbol)
        else:
            print(f'we are in a losing position of {perc}... but we max_loss is not yet achieved')
    else:
        print('we are not in position')

    print(f'for {symbol} just finished checking PNL close...')

    return pnlclose, in_pos, size, long

        
# size kill
def size_kill():
    max_risk = 20

    params = {'type':"swap", "code":"USD"}
    all_bitget_balance = bitget.fetch_balance(params=params)
    open_positions = all_bitget_balance['info']['data']['positions']
    #print(open_positions)

    try:
        pos_cost = open_positions[0]['posCost']
        pos_cost = float(pos_cost)
        openpos_side = open_positions[0]['side']
        openpos_size = open_positions[0]['size']
    except:
        pos_cost = 0
        openpos_side = 0
        openpos_size = 0
    print(f'position cost: {pos_cost}')
    print(f'openpos_side: {openpos_side}')

    if pos_cost > max_risk:
        print(f'EMERGENCY KILL SWITCH ACTIVATED DUE TO CURRENT POSITION SIZE OF {pos_cost} OVER MAX RISK OF {max_risk}')
        kill_switch(symbol) # just calling the kill switch because the trading code section has an error
        time.sleep(30000)
    else:
        print(f'size kill check: current position cost is: {pos_cost}')


