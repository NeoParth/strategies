####### Coding trading bot #1 - sma bot w/ob data

import ccxt
import pandas as pd
import nupmy as np
import key_file
from datetime import date, datetime, timezone, tzinfo
import time, schedule


bitget = ccxt.bitget({
    'enableRateLimit': True,
    'apiKey': ds.xP_hmv_KEY,
    'secret': ds.xP_hmv_SECRET
})


symbol = 'uBTCUSD'
pos_size = 30
params = {'timeInForce': 'PostOnly'}
target = 25
max_lodd = -9
vol_decimal = .4


# ask_bid
def ask_bid(symbol=symbol):
    ob = bitget.fetch_order_book(symbol)

    bid = ob['bids'][0][0]
    ask = ob['asks'][0][0]
# f literal
    print(f'this is the ask for {symbol} {ask}')
    return ask, bid # ask_bid()[0] = ask, [1] = bid 


timeframe = '1d'
limit = 100
sma = 20

def df_sma1(symbol=symbol, timeframe=timeframe, limit=limit, sma=sma):
    print('starting indis...')

    timeframe = '1d'
    num_bars = 100
    sma = 20

    bars = bitget.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    #print(bars)

    df_sma = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    # DAILY SMA - 20 day
    df_sma[f'sma{sma}_{timeframe}'] = df_sma.close.rolling(sma).mean()

    # if bid < the 20 day sma then = BEARISH, if bid > 20 sam = BULLISH
    bid = ask_bid(symbol)[1]

    # if sma > bid = SELL, if sma < bid BUY
    df_sma.loc[df_sma[f'sma{sma}_{timeframe}']>bid, 'sig'] = 'SELL'
    df_sma.loc[dr_sma[f'sma{sma}_{timeframe}']<bid, 'sig'] = 'BUY'

    #print(df_sma)
    return df_sma

timeframe = '15m'
limit = 100
sma = 20
def df_sma(symbol=symbol, timeframe=timeframe, limit=limit, sma=sma):
    print('starting indis...')
    bars = bitget.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    #print(bars)

    df_sma = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    # DAILY SMA - 20 day
    df_sma[f'sma{sma}_{timeframe}'] = df_sma.close.rolling(sma).mean()

    # if bid < the 20 day sma then = BEARISH, if bid > 20 sam = BULLISH
    bid = ask_bid(symbol)[1]

    # if sma > bid = SELL, if sma < bid BUY
    df_sma.loc[df_sma[f'sma{sma}_{timeframe}']>bid, 'sig'] = 'SELL'
    df_sma.loc[dr_sma[f'sma{sma}_{timeframe}']<bid, 'sig'] = 'BUY'

    df_sma['support'] = df_sma[:-2]['close'].min()
    df_sma['resis'] = df_sma[:-2]['close'].max()

    #print(df_sma)
    return df_sma




# open positions.
def open_positions(symbol=symbol):
# what is the pooisition index for that symbol?
    if symbol == 'uBTCSUSD':
        index_pos = 4

        # other symbols, symbol indexes are different on other exchanges

    params = {'type':'swap', 'code':'USD'}
    phe_bal = bitget.fetch_balance(params=params)
    open_positions = phe_bal['info']['data']['positions']
        #print(open_positions)
    openpos_side = open_positions[index_pos]['side'] 
    openpos_size = open_positions[index_pos]['size']
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
        long = open_positions(symbol)[3]
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



def sleep_on_close():
    '''
    this func pulls closed orders, then if last close was in last 59 min
    then it sleeps for 1m
    sincelasttrade = minutes since last trade
    '''
    closed_orders = bitget.fetch_closedorders(symbol)
    for ord in closed_orders[-1::-1]:
        sincelasttrade = 59
        filled = False
        status = ord['info']['ordStatus']
        txttime = ord['info']['transactTimeNs']
        txttime = int(txttime)
        txttime = round((txttime/1000000000)) # bc in nanoseconds
        print(f'this s the status of the order: {status} with epoch {txttime}')
        print('next iteration...')
        print('------')

        if status == 'Filled':
            print('FOUND the order with last fill..')
            print(f'this is the time {txttime} this is the orderstatus {status}')
            orderbook = bitget.fetch_order_book(symbol)
            ex_timestamp = orderbook['timestamp'] # in ms
            ex_timestamp = int(ex_timestamp/1000)
            print('---- below is the transactoin time then exchange epoch')
            print(txttime)

            time_spread = (ex_timestamp - txttime)/60

            if time_spread < sincelasttrade:
                sleepy = round(sincelasttrade - time_spread)*60
                sleepy_min = sleepy/60

                print(f'the time spread is less than {sincelasttrade} mins')
                time.sleep(60)

            else:
                print(f'ist been {time_spread} mins since last fill so no more sleeping')
            break
        else:
            continue
    print('done with the sleep on close function.. ')

def ob():
    print('fetching order book data...')

    df = pd.DataFrame()
    temp_df = pd.DataFrame()

    ob = bitget.fetch_order_book(symbol)

    bids = ob['bids']
    asks = ob['asks']

    first_bid = bids[0]
    first_ask = asks[0]

    bid_vol_list = []
    ask_vol_list = []

    # if SELL vol > Buy vol AND  profit target hit, exit

    # get last 1 min of volume.. and if sell > buy vol do x

    for x in range(11):
        for set in bids:
            price = set[0]
            vol = set[1]
            bid_vol_list.append(vol)

            sum_bidvol = sum(bid_vol_list)
            temp_df['bid_vol'] = [sum_askvol]

            time.sleep(5)
            df = df.apend(temp_df)
            print(df)
            print(' ')
            print('------')
            print(' ')
        print('done collecting volume data for bids and asks...')
        print('calculating the sums...')
        total_bidvol = df['bid_vol'].sum()
        total_askvol = df['ask_vol'].sum()
        print(f'last 1m this is total Bid Vol: {total_bidvol} | ask vol: {total_bidvol}')

        if total_bidvol > total_askvol:
            control_dec = (total_askvol/total_bidvol)
            print(f'Bulls are in control: {control_dec...}')
            # if bulls are in control use regular target
            bullish = True
        else:
            control_dec = (total_bidvol / total_askvol)
            print(f'Bears are in control: {control_dec}...')
            bullish = False
            # .2, .36, .2, .18, .4, .74, .24, .54

        open_posi = open_positions()
        openpos_tf = open_posi[1]
        long = open_posi[3]
        print(f'openpos_tf: {openpos_tf} || long: {long}')

    

        if openpos_tf == True:
            if long == True:
                print('we are in a long position...')
                if control_dec < vol_decimal:
                    vol_under_dec = True
                else:
                    print('volume is NOT under dec so setting vol_under_dec to false')
                    vol_under_dec = False
            else:
                print('we are in a short position...')
                if control_dec < vol_decimal:
                    vol_under_dec = True
                else:
                    print('volume is not under dec so settin vol_under_dec to false')
                    vol_under_dec = False
        else:
            print('we are not in position...')
        
        print(vol_under_dec)

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


def bot():
    pnl_close() # checking if we hit out pnl
    sleep_on_close() # checking sleep on close

    df_d = df_sma1 # determines LONG/SHORT
    df_f = f15_sma() # provides prices bp_1, bp_2, sp_1, sp_2
    ask = ask_bid()[0]
    bid = ask_bid()[1]

    # MAKE OPEN ORDER
    # LONG OR SHORT?
    sig = df_d.iloc[-1]['sig']
    
    open_size = pos_size/2

    # ONLY RUN IF NOT IN POSITION
    # pnl_close() [0] pnlclose and [1] in_pos
    in_pos = pnl_close()[1]
    print(in_pos)
    curr_size = open_positions()[2]
    curr_size = int(curr_size)
    print(curr_size)

    curr_p = bid
    last_sma15 = df_f.iloc[-1]['sma20_15']
    # pos_size = 50 , if inpos == False

    # never get in a position bigger than pos_size (52)
    if ( in_pos == False) and (curr_size < pos_size):
        bitget.cancel_all_orders(symbol)

        # fix order function so I stop sending orders in if price > sma
        if (sig == 'BUY') and (curr_p > last_sma15):
            
            # buy sma daily is < price == BUY
            print('making an opening order as a BUY')
            bp_1 = df_f.iloc[-1]['bp_1']
            bp_2 = df_f.iloc[-1]['bp_2']
            print(f'this is bp_2: {bp_1} this is bp_2: {bp_2}')
            bitget.cancel_all_orders(symbol)
            bitget.create_limit_buy_order(symbol, open_size, bp_1, params)
            bitget.create_limit_buy_order(symbol, open_size, bp_2, params)

            print('just made opening order so going to sleep for 2mins...')
            time.sleep(120)

        elif (sig == 'SELL') and (curr_p < last_sma15):
            print('making an opening order as a SELL')
            sp_1 = df_f.iloc[-1]['sp_1']
            sp_2 = df_f.iloc[-1]['sp_2']
            print(f'this is sp_1: {sp_1} this is sp_2 {sp_2}')
            bitget.cancel_all_orders(symbol)
            bitget.create_limit_sell_order(symbol, open_size, sp_1, params)
            bitget.create_limit_sell_order(symbol, open_size, sp_2, params)

            print('just made opening order so going to sleep for 2mins...')
            time.sleep(120)

        else:
            print('not submitting orders..price prob higher or lower than sma.. sleep for 10mins')
            time.sleep(600)
    
    schedule.every(28).seconds.do(bot)

    while True:
        try:
            schedule.run_pending()
        except:
            print('+++++ MAYBE AN INTERNET PROBLEM OR SOMETHING ELSE +++++')
            time.sleep(30)


