#!/usr/bin/env python3
"""
Script to check if order book data is actually stored in the Redis cluster
"""

import redis
from redis.cluster import RedisCluster, ClusterNode
import json
import time
from datetime import datetime

def connect_redis():
    """Connect to Redis cluster"""
    try:
        r = RedisCluster(
            startup_nodes=[
                ClusterNode("127.0.0.1", 7000),
                ClusterNode("127.0.0.1", 7001),
                ClusterNode("127.0.0.1", 7002),
            ],
            decode_responses=True,
        )
        return r
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return None

def check_basic_redis_operations(r):
    """Test basic Redis operations"""
    print("🔍 Testing basic Redis operations...")
    try:
        # Test set/get
        r.set("test_key", "test_value", ex=10)
        value = r.get("test_key")
        r.delete("test_key")
                
        if value == "test_value":
            print("✅ Basic Redis operations working")
            return True
        else:
            print("❌ Basic Redis operations failed")
            return False
    except Exception as e:
        print(f"❌ Basic Redis test failed: {e}")
        return False

def check_orderbook_keys(r):
    """Check for orderbook keys in Redis"""
    print("\n🔍 Checking for orderbook keys...")
    try:
        # Get all keys matching orderbook pattern
        keys = r.keys("orderbook:*")
        print(f"Found {len(keys)} orderbook keys")
        
        if keys:
            print("\nSample keys:")
            for i, key in enumerate(keys[:10]):  # Show first 10
                print(f"  {i+1}. {key}")
            
            # Show detailed info for first few keys
            print("\n📊 Detailed data for first 3 keys:")
            for i, key in enumerate(keys[:3]):
                try:
                    data = r.zrange(key, 0, -1, withscores=True)
                    ttl = r.ttl(key)
                    print(f"\n  Key: {key}")
                    print(f"    TTL: {ttl} seconds")
                    print(f"    Data: {data}")
                    
                    if data:
                        # Parse the data
                        member = data[0][0]  # JSON string
                        score = data[0][1]   # Price
                        try:
                            json_data = json.loads(member)
                            quantity = json_data.get('q', 'N/A')
                            print(f"    Price: {score}")
                            print(f"    Quantity: {quantity}")
                        except:
                            print(f"    Raw member: {member}")
                            print(f"    Score: {score}")
                except Exception as e:
                    print(f"    Error reading {key}: {e}")
        else:
            print("❌ No orderbook keys found!")
            print("This means:")
            print("  1. The order book data collection script is not running")
            print("  2. The script is running but not storing data")
            print("  3. The data has expired (TTL)")
            print("  4. There's an issue with the Redis connection")
        
        return keys
    except Exception as e:
        print(f"❌ Error checking orderbook keys: {e}")
        return []

def check_specific_symbol(r, symbol="BTC/USDT"):
    """Check data for a specific symbol"""
    print(f"\n🔍 Checking data for {symbol}...")
    
    exchanges = ['binance', 'bitget', 'bybit', 'coinex', 'huobi', 'kucoin', 'mexc']
    
    for exchange in exchanges:
        bid_key = f"orderbook:{{{symbol}}}:{exchange}:bid"
        ask_key = f"orderbook:{{{symbol}}}:{exchange}:ask"
        
        try:
            bid_data = r.zrange(bid_key, 0, -1, withscores=True)
            ask_data = r.zrange(ask_key, 0, -1, withscores=True)
            bid_ttl = r.ttl(bid_key)
            ask_ttl = r.ttl(ask_key)
            
            if bid_data and ask_data:
                bid_price = bid_data[0][1]
                ask_price = ask_data[0][1]
                spread = ask_price - bid_price
                spread_pct = (spread / bid_price) * 100
                
                print(f"  ✅ {exchange:10} | Bid: {bid_price:12.6f} | Ask: {ask_price:12.6f} | "
                      f"Spread: {spread:8.6f} ({spread_pct:5.2f}%) | TTL: {bid_ttl}s")
            else:
                print(f"  ❌ {exchange:10} | No data available")
                
        except Exception as e:
            print(f"  ❌ {exchange:10} | Error: {str(e)[:30]}...")

def check_redis_info(r):
    """Get Redis cluster information"""
    print("\n📈 Redis Cluster Information:")
    try:
        info = r.info()
        print(f"  Connected clients: {info.get('connected_clients', 'N/A')}")
        print(f"  Used memory: {info.get('used_memory_human', 'N/A')}")
        print(f"  Total commands processed: {info.get('total_commands_processed', 'N/A')}")
        print(f"  Keyspace hits: {info.get('keyspace_hits', 'N/A')}")
        print(f"  Keyspace misses: {info.get('keyspace_misses', 'N/A')}")
    except Exception as e:
        print(f"  ❌ Could not get cluster info: {e}")

def monitor_data_changes(r, duration=30):
    """Monitor data changes for a period"""
    print(f"\n👀 Monitoring data changes for {duration} seconds...")
    print("Press Ctrl+C to stop early")
    
    try:
        start_time = time.time()
        initial_keys = len(r.keys("orderbook:*"))
        print(f"Initial keys: {initial_keys}")
        
        while time.time() - start_time < duration:
            current_keys = len(r.keys("orderbook:*"))
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Keys: {current_keys}")
            
            if current_keys > initial_keys:
                print(f"  📈 New data detected! (+{current_keys - initial_keys} keys)")
                initial_keys = current_keys
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")

def main():
    """Main function"""
    print("🚀 Redis Data Checker")
    print("=" * 50)
    
    # Connect to Redis
    r = connect_redis()
    if not r:
        return
    
    # Test basic operations
    if not check_basic_redis_operations(r):
        print("❌ Cannot proceed without basic Redis functionality")
        return
    
    # Check Redis info
    check_redis_info(r)
    
    # Check for orderbook keys
    keys = check_orderbook_keys(r)
    
    # Check specific symbol if keys exist
    if keys:
        check_specific_symbol(r, "BTC/USDT")
        
        # Ask if user wants to monitor
        print("\n" + "=" * 50)
        response = input("Monitor data changes for 30 seconds? (y/n): ")
        if response.lower() == 'y':
            monitor_data_changes(r, 30)
    else:
        print("\n💡 To get data:")
        print("  1. Make sure Redis cluster is running")
        print("  2. Run: python order-book-data.py")
        print("  3. Wait a few seconds for data to accumulate")
        print("  4. Run this script again to check")

if __name__ == "__main__":
    main() 