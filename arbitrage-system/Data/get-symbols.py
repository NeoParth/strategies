import ccxt
import csv
from collections import Counter
import time

print("Starting script...")

# Gather all tickers from each exchange
exchange_currencies = []

# Each exchange has different API structures
exchanges = [
    ('binance', ccxt.binance()),
    ('bitget', ccxt.bitget()),
    ('kucoin', ccxt.kucoin()),
    ('mexc', ccxt.mexc()),
    ('bybit', ccxt.bybit()),
    ('huobi', ccxt.huobi()),
    ('coinex', ccxt.coinex())
]

print(f"Processing {len(exchanges)} exchanges...")

for name, exchange in exchanges:
    try:
        print(f"Fetching currencies from {name}...")
        
        # Enable rate limiting to avoid being blocked
        exchange.enableRateLimit = True
        
        # Different exchanges have different methods to get currencies
        if name in ['binance', 'mexc', 'okx', 'bybit']:
            # These exchanges don't have fetchCurrencies, use fetchMarkets instead
            try:
                markets = exchange.fetchMarkets()
                # Extract base currencies from market pairs
                tickers = set()
                for market in markets:
                    if market['base']:
                        tickers.add(market['base'])
                print(f"Found {len(tickers)} currencies on {name} via markets")
            except Exception as e:
                print(f"Error fetching markets from {name}: {e}")
                tickers = set()
        else:
            # Other exchanges might have fetchCurrencies
            try:
                currencies = exchange.fetchCurrencies()
                tickers = set(currencies.keys())
                print(f"Found {len(tickers)} currencies on {name} via fetchCurrencies")
            except Exception as e:
                print(f"Error with fetchCurrencies from {name}, trying fetchMarkets: {e}")
                # Fallback to fetchMarkets
                try:
                    markets = exchange.fetchMarkets()
                    tickers = set()
                    for market in markets:
                        if market['base']:
                            tickers.add(market['base'])
                    print(f"Found {len(tickers)} currencies on {name} via fallback markets")
                except Exception as e2:
                    print(f"Error fetching markets from {name}: {e2}")
                    tickers = set()
        
        exchange_currencies.append(tickers)
        
        # Add a small delay between exchanges to be respectful
        time.sleep(1)
        
    except Exception as e:
        print(f"Error processing {name}: {e}")
        exchange_currencies.append(set())

print(f"Total exchange_currencies lists: {len(exchange_currencies)}")

# Count how many exchanges each ticker appears on
all_tickers = [ticker for tickers in exchange_currencies for ticker in tickers]
print(f"Total unique tickers found: {len(set(all_tickers))}")
ticker_counts = Counter(all_tickers)

# Filter tickers that are available on at least 2 exchanges
common_tickers = [ticker for ticker, count in ticker_counts.items() if count >= 2]
print(f"Tickers available on at least 2 exchanges: {len(common_tickers)}")

# Write to tokens.csv
print("Writing to tokens.csv...")
with open('tokens.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['token'])  # header
    for ticker in sorted(common_tickers):
        writer.writerow([ticker])

print(f"Saved {len(common_tickers)} tokens available on at least 2 exchanges to tokens.csv")

# Print some sample common tokens
if common_tickers:
    print(f"Sample common tokens: {sorted(common_tickers)[:10]}")
    print(f"Sample common tokens: {sorted(common_tickers)[:10]}")
