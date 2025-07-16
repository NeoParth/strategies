#!/usr/bin/env python3
import time, json, ccxt
from redis.cluster import RedisCluster         # import from redis-py-cluster :contentReference[oaicite:0]{index=0}
from redis.cluster import ClusterNode
import key_file

# Load symbols
SYMBOLS = open("tokens.csv").read().splitlines()
TTL     = 60


r = RedisCluster(
    startup_nodes=[
        ClusterNode("127.0.0.1", 7000),
        ClusterNode("127.0.0.1", 7001),
        ClusterNode("127.0.0.1", 7002),
    ],
    decode_responses=True,
)



# CCXT exchanges
exs = {
    'binance': ccxt.binance({ 'apiKey': key_file.BINANCE_API_KEY, 'secret': key_file.BINANCE_SECRET, 'enableRateLimit': True }),
    'bitget':  ccxt.bitget({  'apiKey': key_file.BITGET_API_KEY,  'secret': key_file.BITGET_SECRET,  'password': key_file.BITGET_PASSPHRASE, 'enableRateLimit': True }),
    'bybit':   ccxt.bybit({   'apiKey': key_file.BYBIT_API_KEY,   'secret': key_file.BYBIT_SECRET,   'enableRateLimit': True }),
    'coinex':  ccxt.coinex({  'apiKey': key_file.COINEX_API_KEY,  'secret': key_file.COINEX_SECRET,  'enableRateLimit': True }),
    'huobi':   ccxt.huobi({   'apiKey': key_file.HUOBI_API_KEY,   'secret': key_file.HUOBI_SECRET,   'enableRateLimit': True }),
    'kucoin':  ccxt.kucoin({  'apiKey': key_file.KUCOIN_API_KEY,  'secret': key_file.KUCOIN_SECRET,  'password': key_file.KUCOIN_PASSPHRASE, 'enableRateLimit': True }),
    'mexc':    ccxt.mexc({    'apiKey': key_file.MEXC_API_KEY,    'secret': key_file.MEXC_SECRET,    'enableRateLimit': True }),
}

def store_top(symbol, exch, book):
    bid, ask = book['bids'][0], book['asks'][0]
    bkey = f"orderbook:{{{symbol}}}:{exch}:bid"
    akey = f"orderbook:{{{symbol}}}:{exch}:ask"
    pipe = r.pipeline()                        # cluster pipelines supported :contentReference[oaicite:2]{index=2}
    pipe.zadd(bkey, {json.dumps({'q': bid[1]}): bid[0]})
    pipe.expire(bkey, TTL)
    pipe.zadd(akey, {json.dumps({'q': ask[1]}): ask[0]})
    pipe.expire(akey, TTL)
    pipe.execute()

if __name__ == "__main__":
    while True:
        t0 = time.time()
        for sym in SYMBOLS:
            for name, ex in exs.items():
                try:
                    ob = ex.fetch_order_book(sym, limit=1)
                    store_top(sym, name, ob)
                except Exception as e:
                    print(f"[Ingest] {name}/{sym} error: {e}")
        elapsed = time.time() - t0
        time.sleep(max(0, 1.0 - elapsed))
