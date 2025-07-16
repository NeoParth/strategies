#!/usr/bin/env python3
from redis.cluster import RedisCluster
import json

# Connect to the same cluster
r = RedisCluster(
    startup_nodes=[
        {"host":"127.0.0.1","port":"7000"},
        {"host":"127.0.0.1","port":"7001"},
        {"host":"127.0.0.1","port":"7002"},
    ],
    decode_responses=True,
)

# Scan across the cluster for any orderbook keys
print("Scanning for orderbook keys across all shards...")
keys = list(r.scan_iter(match="orderbook:*"))
print(f"Found {len(keys)} keys:")
for k in keys[:20]:
    print("  ", k)
if len(keys) == 0:
    print("⚠️ No keys found! Ingest script may not be running or writing correctly.")
else:
    print("✅ Ingest is populating keys as expected.")
