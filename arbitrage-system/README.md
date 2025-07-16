This Model exploits price inefficiencies on CEX and DEXs* in crypto

*currently DEXs are incorporated only by hand. In the future we plan to build own API connections and web-sockets to include also the Decentralized Exchanges

Strategy by: Lukas Kofler
Implemented by: Luis Parth

->

# Arbitrage Trading System

This system exploits price inefficiencies across multiple cryptocurrency exchanges (CEX) to identify and execute arbitrage opportunities.

**Strategy by:** Lukas Kofler  
**Implemented by:** Luis Parth

## 🎯 Overview

The arbitrage system monitors 8 major cryptocurrency exchanges in real-time to identify price differences that can be exploited for profit. It works by:

1. **Symbol Discovery**: Finding common tokens across all exchanges
2. **Order Book Monitoring**: Continuously fetching real-time order books
3. **Arbitrage Detection**: Scanning for profitable price differences
4. **Opportunity Reporting**: Displaying actionable arbitrage opportunities

## 🏗️ System Architecture

### Components

1. **`get-symbols.py`** - Discovers common tokens across exchanges
2. **`fetch_orderbooks.py`** - Fetches real-time order book data
3. **`arbitrage_scanner.py`** - Identifies arbitrage opportunities
4. **`run_arbitrage_system.py`** - Main orchestrator script
5. **`config.py`** - Configuration and Redis setup

### Supported Exchanges

- Binance
- Bitget
- KuCoin
- MEXC
- OKX
- Bybit
- Huobi
- CoinEx

## 🚀 Quick Start

### Prerequisites

1. **Redis Server**: Must be running locally
2. **Python Dependencies**: Install required packages
3. **API Keys**: Configure exchange API keys in `security/key_file.py`

### Installation

```bash
# Install dependencies
pip install ccxt redis

# Start Redis server
redis-server

# Configure API keys in security/key_file.py
```

### Running the System

```bash
# Navigate to the Data directory
cd strategies/arbitrage-system/Data

# Run the complete system
python run_arbitrage_system.py

# Or run with custom parameters
python run_arbitrage_system.py --min-profit 1.0 --scan-interval 60
```

## 📊 How It Works

### 1. Symbol Discovery
- Fetches all available trading pairs from each exchange
- Identifies tokens available on at least 2 exchanges
- Saves common tokens to `tokens.csv`

### 2. Order Book Monitoring
- Continuously fetches order books for all symbols
- Stores data in Redis with 90-second TTL
- Uses concurrent processing for efficiency

### 3. Arbitrage Detection
- Compares bid/ask prices across exchanges
- Calculates potential profit percentages
- Identifies opportunities above minimum threshold
- Reports detailed trade instructions

### 4. Data Flow
```
Exchanges → Order Books → Redis → Scanner → Opportunities
```

## ⚙️ Configuration

### Redis Settings
- **TTL**: 90 seconds (order book data freshness)
- **Connection**: Local Redis instance
- **Data Structure**: Sorted sets for bids/asks

### Trading Parameters
- **Minimum Profit**: Configurable percentage (default: 0.5%)
- **Scan Interval**: How often to check for opportunities
- **Order Book Depth**: Top 5 levels per side

## 📈 Arbitrage Opportunities

The system identifies two types of arbitrage:

1. **Buy-Sell Arbitrage**: Buy on exchange A, sell on exchange B
2. **Reverse Arbitrage**: Buy on exchange B, sell on exchange A

### Opportunity Output Example
```
🚀 ARBITRAGE OPPORTUNITY #1
Symbol: BTC
Strategy: Buy on binance @ $43,250.50
         Sell on kucoin @ $43,280.75
Profit per unit: $30.25
Profit percentage: 0.07%
Max quantity: 0.5
Total profit: $15.13
Timestamp: 2024-01-15 14:30:25
```

## 🔧 Customization

### Adjusting Parameters
- Modify `min_profit_percentage` for different profit thresholds
- Change `scan_interval` for different monitoring frequencies
- Update `TTL` in config.py for different data freshness

### Adding Exchanges
1. Add exchange configuration to `config.py`
2. Update exchange list in `get-symbols.py`
3. Add API keys to `security/key_file.py`

## ⚠️ Important Notes

- **API Rate Limits**: System includes rate limiting to avoid exchange bans
- **Data Freshness**: Only uses data within TTL window
- **Risk Management**: Always verify opportunities before trading
- **Fees**: Consider trading fees when calculating actual profit

## 🛠️ Troubleshooting

### Common Issues
1. **Redis Connection Error**: Ensure Redis server is running
2. **API Key Errors**: Verify API keys in `security/key_file.py`
3. **Rate Limiting**: System automatically handles rate limits
4. **No Opportunities**: Lower minimum profit threshold or wait for market volatility

### Logs and Monitoring
- Check console output for real-time status
- Monitor Redis memory usage
- Review error messages for troubleshooting