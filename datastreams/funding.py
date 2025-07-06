import asyncio
import json
from datetime import datetime
from websockets import connect
from termcolor import cprint

symbols = ['btcusdt', 'xrpusdt', 'ethusdt', 'solusdt', 'wifusdt']
websocket_url_base = 'wss://fstream.binance.com/ws/'

# 1) instantiate the lock properly
print_lock = asyncio.Lock()

async def binance_funding_stream(symbol, shared_counter):
    websocket_url = f'{websocket_url_base}{symbol}@markPrice'
    async with connect(websocket_url) as websocket:
        while True:
            try:
                # 2) actually acquire the lock here
                async with print_lock:
                    message = await websocket.recv()
                    data = json.loads(message)
                    event_time = datetime.fromtimestamp(data['E'] / 1000).strftime("%H:%M:%S")
                    symbol_display = data['s'].replace('USDT', '').upper()
                    funding_rate = float(data['r'])
                    yearly_funding_rate = funding_rate * 3 * 365 * 100

                    # color logic unchanged...
                    if yearly_funding_rate > 50:
                        text_color, back_color = 'grey ', 'on_red'
                    elif yearly_funding_rate > 30:
                        text_color, back_color = 'grey', 'on_yellow'
                    elif yearly_funding_rate > 5:
                        text_color, back_color = 'grey', 'on_cyan'
                    elif yearly_funding_rate > -10:
                        text_color, back_color = 'grey', 'on_white'
                    else:
                        text_color, back_color = 'grey', 'on_red'

                    cprint(f"{symbol_display} funding: {yearly_funding_rate:.2f}%", text_color, back_color)

                    shared_counter['count'] += 1

                    # 3) compare to len(symbols), not len(symbol)
                    if shared_counter['count'] >= len(symbols):
                        cprint(f"{event_time} yrly fund summary", 'white', 'on_grey')
                        shared_counter['count'] = 0

            except Exception as e:
                # It's better to at least log the exception
                print(f"Error in {symbol}: {e!r}, retrying in 5s…")
                await asyncio.sleep(5)

async def main():
    # pass the same lock and counter to all tasks
    shared_symbol_counter = {'count': 0}
    tasks = [binance_funding_stream(sym, shared_symbol_counter) for sym in symbols]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
