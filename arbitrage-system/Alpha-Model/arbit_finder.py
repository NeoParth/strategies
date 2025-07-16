#!/usr/bin/env python3
import time
from rediscluster import RedisCluster         # same import here :contentReference[oaicite:3]{index=3}

# Connect to cluster
print("🔌 Connecting to Redis cluster...")
try:
    r = RedisCluster(
        startup_nodes=[
            {"host": "127.0.0.1", "port": "7000"},
            {"host": "127.0.0.1", "port": "7001"},
            {"host": "127.0.0.1", "port": "7002"},
        ],
        decode_responses=True,
    )
    # Test connection
    r.set("test_arbit", "working", ex=10)
    test_val = r.get("test_arbit")
    r.delete("test_arbit")
    if test_val == "working":
        print("✅ Redis cluster connection successful")
    else:
        print("❌ Redis cluster connection failed")
        exit(1)
except Exception as e:
    print(f"❌ Failed to connect to Redis cluster: {e}")
    exit(1)

EXCHANGES = ['binance','bitget','bybit','coinex','huobi','kucoin','mexc']
THRESHOLD = 0.5

def get_top(symbol, exch):
    """Get top of book for a symbol on an exchange"""
    try:
        bid_key = f"orderbook:{{{symbol}}}:{exch}:bid"
        ask_key = f"orderbook:{{{symbol}}}:{exch}:ask"
        
        print(f"🔍 Fetching {symbol} on {exch}...")
        print(f"   Bid key: {bid_key}")
        print(f"   Ask key: {ask_key}")
        
        bids = r.zrevrange(bid_key, 0, 0, withscores=True)
        asks = r.zrange(ask_key, 0, 0, withscores=True)
        
        print(f"   Raw bids: {bids}")
        print(f"   Raw asks: {asks}")
        
        # Fix: Handle empty lists properly to avoid IndexError
        try:
            best_bid = bids[0][1] if bids else None
        except (IndexError, TypeError):
            best_bid = None
            
        try:
            best_ask = asks[0][1] if asks else None
        except (IndexError, TypeError):
            best_ask = None
        
        print(f"   Processed bid: {best_bid}")
        print(f"   Processed ask: {best_ask}")
        
        return best_bid, best_ask
        
    except Exception as e:
        print(f"❌ Error getting top of book for {symbol} on {exch}: {e}")
        return None, None

def find_arb(symbol):
    """Find arbitrage opportunities for a symbol"""
    print(f"\n🔍 Scanning for arbitrage opportunities: {symbol}")
    opps = []
    
    for b in EXCHANGES:
        for s in EXCHANGES:
            if b == s: 
                continue
                
            print(f"\n  Comparing {b} (buy) vs {s} (sell) for {symbol}")
            
            bid, _ = get_top(symbol, s)  # Best bid on sell exchange
            _, ask = get_top(symbol, b)  # Best ask on buy exchange
            
            print(f"    Best bid on {s}: {bid}")
            print(f"    Best ask on {b}: {ask}")
            
            if bid and ask:
                spread = bid - ask
                print(f"    Spread: {spread:.6f} (threshold: {THRESHOLD})")
                
                if spread >= THRESHOLD:
                    print(f"    ✅ ARBITRAGE FOUND!")
                    opps.append((symbol, b, s, spread))
                else:
                    print(f"    ❌ Spread too small")
            else:
                print(f"    ❌ Missing bid or ask data")
    
    print(f"\n📊 Found {len(opps)} arbitrage opportunities for {symbol}")
    return opps

def check_redis_data():
    """Check what data is available in Redis"""
    print("\n🔍 Checking Redis data availability...")
    
    try:
        # Get all orderbook keys
        keys = r.keys("orderbook:*")
        print(f"Total orderbook keys in Redis: {len(keys)}")
        
        if keys:
            print("Sample keys:")
            for i, key in enumerate(keys[:10]):  # Show first 10 keys
                print(f"  {i+1}. {key}")
            
            # Check a specific key
            if keys:
                sample_key = keys[0]
                print(f"\nSample data from {sample_key}:")
                data = r.zrange(sample_key, 0, -1, withscores=True)
                print(f"  Data: {data}")
        else:
            print("❌ No orderbook data found in Redis!")
            print("Make sure the order book data collection script is running")
            
    except Exception as e:
        print(f"❌ Error checking Redis data: {e}")

if __name__ == "__main__":
    print("🚀 Starting Arbitrage Finder")
    print("=" * 50)
    
    # Check Redis data first
    check_redis_data()
    
    try:
        SYMBOLS = open("tokens.csv").read().splitlines()
        print(f"\n📋 Loaded {len(SYMBOLS)} symbols from tokens.csv")
        print(f"Symbols: {SYMBOLS[:5]}...")  # Show first 5 symbols
    except FileNotFoundError:
        print("❌ tokens.csv not found!")
        print("Creating sample symbols for testing...")
        SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    except Exception as e:
        print(f"❌ Error reading tokens.csv: {e}")
        SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    
    print(f"\n🔍 Testing with exchanges: {EXCHANGES}")
    print(f"💰 Minimum spread threshold: {THRESHOLD}")
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}")
        print("-" * 30)
        
        opportunities_found = 0
        
        for sym in SYMBOLS:
            try:
                opps = find_arb(sym)
                for symbol, buy, sell, spread in opps:
                    print(f"🎯 ARBITRAGE: {symbol} buy@{buy} sell@{sell} spread={spread:.4f}")
                    opportunities_found += 1
            except Exception as e:
                print(f"❌ Error processing {sym}: {e}")
        
        if opportunities_found == 0:
            print(f"⏰ No arbitrage opportunities found in iteration {iteration}")
        
        print(f"\n⏳ Waiting 1 second before next scan...")
        time.sleep(1)
