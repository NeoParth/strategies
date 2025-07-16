# Redis CLI Commands to Check Order Book Data

## Connect to Redis Cluster

```bash
# Connect to any node in the cluster
redis-cli -p 7000
redis-cli -p 7001
redis-cli -p 7002
```

## Basic Commands to Check Data

### 1. Check if Redis is working
```redis
PING
```
Should return: `PONG`

### 2. List all orderbook keys
```redis
KEYS "orderbook:*"
```

### 3. Count total orderbook keys
```redis
KEYS "orderbook:*" | wc -l
```

### 4. Check specific symbol data
```redis
# For BTC/USDT on Binance
ZRANGE "orderbook:{BTC/USDT}:binance:bid" 0 -1 WITHSCORES
ZRANGE "orderbook:{BTC/USDT}:binance:ask" 0 -1 WITHSCORES
```

### 5. Check TTL (time to live) of keys
```redis
TTL "orderbook:{BTC/USDT}:binance:bid"
TTL "orderbook:{BTC/USDT}:binance:ask"
```

### 6. Get cluster info
```redis
INFO
```

### 7. Check memory usage
```redis
INFO memory
```

### 8. Monitor all commands in real-time
```redis
MONITOR
```

## Example Session

```bash
# Connect to Redis
redis-cli -p 7000

# Check if working
127.0.0.1:7000> PING
PONG

# List all orderbook keys
127.0.0.1:7000> KEYS "orderbook:*"
1) "orderbook:{BTC/USDT}:binance:bid"
2) "orderbook:{BTC/USDT}:binance:ask"
3) "orderbook:{BTC/USDT}:bitget:bid"
4) "orderbook:{BTC/USDT}:bitget:ask"
...

# Check specific data
127.0.0.1:7000> ZRANGE "orderbook:{BTC/USDT}:binance:bid" 0 -1 WITHSCORES
1) "{\"q\": 0.1234}"
2) "43250.5"

# Check TTL
127.0.0.1:7000> TTL "orderbook:{BTC/USDT}:binance:bid"
(integer) 45
```

## Troubleshooting Commands

### If no keys found:
```redis
# Check if any keys exist
KEYS "*"

# Check cluster status
CLUSTER INFO

# Check cluster nodes
CLUSTER NODES
```

### If connection fails:
```bash
# Check if Redis is running
ps aux | grep redis

# Check ports
netstat -tlnp | grep :700
```

## Python Script Alternative

Run the Python script I created:
```bash
cd strategies/arbitrage-system/Data
python check_redis_data.py
```

This will give you a comprehensive overview of:
- Redis connection status
- Number of orderbook keys
- Sample data from keys
- TTL information
- Real-time monitoring option 