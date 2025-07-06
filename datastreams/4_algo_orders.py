## Coding Algo Orders ##

# connect exchange #

import ccxt
import key_file as k
import time, schedule

bitget = ccxt.bitget({
    'enableRateLimit': True,
    'apiKey': k.key,
    'secret': k.secret,
})


bal = bitget.fetch_balance()

symbol = 'uBTCUSD'
size = 1
bid = 100000
params = {'timeInForxe': 'PostOnly'}


###################################################################### USEFUL BUILDING BLOCKS ##############################################################################################

# (1) making an order
order = bitget.create_limit_buy_order(symbol, size, bid, params)
print(order)

# (2) sleep 10 seconds before you cancel the order - check if it has gone through - to confirm price, to retry on illiquid markets - elliminates need to click multiple times on the arbitfinder exchanges (use cas implemented in 4.)
print('just made the order - now sleeping 10sec before cancellation')
time.sleep(10)


# (3) cancel order
bitget.cancel_all_orders(symbol)

# (4) Putting it all together - Loop through code - try orders until order has been fulfilled
def bot():
    bitget.create_limit_buy_order(symbol, size, bid, params)
    time.sleep(10)
    bitget.cancel_all_orders(symbol)

schedule.every(28).second.do(bot)

while True:
    try:
        schedule.run_pending()
    except:
        print('+++ Maybe an Internet PROB OR SOMETHING')
        time.sleep(30)