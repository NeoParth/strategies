import os
import key_file as k

# Exchange API configurations
EXCHANGE_CONFIGS = {
    'binance': {
        'apiKey': os.getenv('k.BINANCE_API_KEY'),
        'secret': os.getenv('k.BINANCE_SECRET'),
        'password': None,  # Some exchanges don't need password
        'sandbox': False,  # Set to True for testing
    },
    'bitget': {
        'apiKey': k.BITGET_API_KEY,
        'secret': k.BITGET_SECRET,
        'password': k.BITGET_PASSPHRASE,
        'sandbox': False,
    },
    'kucoin': {
        'apiKey': k.KUCOIN_API_KEY,
        'secret': k.KUCOIN_SECRET,
        'password': k.KUCOIN_PASSPHRASE,
        'sandbox': False,
    },
    'mexc': {
        'apiKey': k.MEXC_API_KEY,
        'secret': k.MEXC_SECRET,
        'password': None,
        'sandbox': False,
    },
    'okx': {
        'apiKey': k.OKX_API_KEY,
        'secret': k.OKX_SECRET,
        'password': k.OKX_PASSPHRASE,
        'sandbox': False,
    },
    'bybit': {
        'apiKey': k.BYBIT_API_KEY,
        'secret': k.BYBIT_SECRET,
        'password': None,
        'sandbox': False,
    },
    'huobi': {
        'apiKey': k.HUOBI_API_KEY,
        'secret': k.HUOBI_SECRET,
        'password': None,
        'sandbox': False,
    },
    'coinex': {
        'apiKey': k.COINEX_API_KEY,
        'secret': k.COINEX_SECRET,
        'password': None,
        'sandbox': False,
    },

} 