"""Example integration test credentials.

Copy this file to `local_credentials.py` and fill in your actual credentials.
The `local_credentials.py` file is gitignored for security.

Usage:
    cp tests/config/credentials.example.py tests/config/local_credentials.py
    # Edit local_credentials.py with your real credentials
"""

# MockExchange configuration
MOCKX_BASE_URL = "http://localhost:8000"  # Your MockExchange instance (default)
MOCKX_API_KEY = "dev-key"  # MockExchange API key

# Exchange configuration (for production mode integration tests)
# You can use any CCXT-supported exchange: binance, coinbase, kraken, etc.
EXCHANGE_ID = "binance"  # Change this to your preferred exchange
EXCHANGE_API_KEY = "your-exchange-api-key-here"
EXCHANGE_SECRET = "your-exchange-secret-here"

# Test configuration
INTEGRATION_CONFIG = {
    "mockexchange": {
        "base_url": MOCKX_BASE_URL,
        "api_key": MOCKX_API_KEY,
        "timeout": 10.0,
    },
    "exchange": {
        "exchange_id": EXCHANGE_ID,
        "api_key": EXCHANGE_API_KEY,
        "secret": EXCHANGE_SECRET,
        "sandbox": True,  # Always use sandbox for tests
        "enableRateLimit": True,
    },
}
