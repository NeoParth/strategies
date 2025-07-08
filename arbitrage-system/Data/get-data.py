import ccxt
import csv
from collections import Counter
from config import EXCHANGE_CONFIGS

print("Starting script...")

# Gather all tickers from each exchange
exchange_currencies = []

# Create exchange instances with API credentials
exchanges = []
for name, config in EXCHANGE_CONFIGS.items():
    try:
        # Create exchange instance with credentials
        exchange_class = getattr(ccxt, name)
        exchange = exchange_class({
            'apiKey': config['apiKey'],
            'secret': config['secret'],
            'password': config.get('password'),  # Some exchanges need this
            'sandbox': config.get('sandbox', False),
            'enableRateLimit': True,  # Important for avoiding rate limits
        })
        exchanges.append((name, exchange))
        print(f"Successfully configured {name}")
    except Exception as e:
        print(f"Error configuring {name}: {e}")

print(f"Processing {len(exchanges)} exchanges...")

for name, exchange in exchanges:
    try:
        print(f"Fetching currencies from {name}...")
        currencies = exchange.fetchCurrencies()
        tickers = set(currencies.keys())
        print(f"Found {len(tickers)} currencies on {name}")
        exchange_currencies.append(tickers)
    except Exception as e:
        print(f"Error fetching currencies from {name}: {e}")
        exchange_currencies.append(set())

print(f"Total exchange_currencies lists: {len(exchange_currencies)}")

# Count how many exchanges each ticker appears on
all_tickers = [ticker for tickers in exchange_currencies for ticker in tickers]
print(f"Total unique tickers found: {len(set(all_tickers))}")
ticker_counts = Counter(all_tickers)

# Filter tickers that are available on at least 2 exchanges
common_tickers = [ticker for ticker, count in ticker_counts.items() if count >= 2]
print(f"Tickers available on at least 2 exchanges: {len(common_tickers)}")

# Write to token.csv
print("Writing to tokens.csv...")
with open('tokens.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['token'])  # header
    for ticker in sorted(common_tickers):
        writer.writerow([ticker])

print(f"Saved {len(common_tickers)} tokens available on at least 2 exchanges to tokens.csv")
