"""examples/error_handling.py

Error handling example for MockX Gateway.

This example demonstrates how to handle different types of errors
that can occur when using the gateway, including NotSupported errors
for features not available in paper mode.
"""

from mockexchange_gateway import (
    AuthenticationError,
    BadSymbol,
    ExchangeError,
    InsufficientFunds,
    NetworkError,
    NotSupported,
    OrderNotFound,
    create_paper_gateway,
)


def demonstrate_error_handling():
    """Demonstrate comprehensive error handling patterns."""
    print("=== Error Handling Example ===")

    # Create gateway
    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # 1. Check capabilities before using features
    print("\n1. Capability Checking:")
    features_to_test = [
        "createOrder",
        "fetchOHLCV",
        "fetchOrderBook",
        "fetchTicker",
        "fetchBalance",
    ]

    for feature in features_to_test:
        if gateway.has.get(feature, False):
            print(f"✅ {feature}: Supported")
        else:
            print(f"❌ {feature}: Not supported")

    # 2. Handle NotSupported errors gracefully
    print("\n2. NotSupported Error Handling:")
    unsupported_features = [
        ("fetchOHLCV", "BTC/USDT", "1h"),
        ("fetchOrderBook", "BTC/USDT"),
        ("fetchTrades", "BTC/USDT"),
    ]

    for method_name, *args in unsupported_features:
        try:
            method = getattr(gateway, method_name)
            result = method(*args)
            print(f"✅ {method_name}: {result}")
        except NotSupported as e:
            print(f"❌ {method_name}: {e}")
        except Exception as e:
            print(f"⚠️  {method_name}: Unexpected error - {e}")

    # 3. Handle network and connection errors
    print("\n3. Network Error Handling:")
    try:
        # This might fail if MockExchange is not running
        markets = gateway.load_markets()
        print(f"✅ Markets loaded: {len(markets)} pairs")
    except NetworkError as e:
        print(f"❌ Network error: {e}")
        print("   Make sure MockExchange is running at http://localhost:8000")
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   Check if MockExchange is accessible")
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")

    # 4. Handle trading-specific errors
    print("\n4. Trading Error Handling:")
    try:
        # Try to place an order (might fail for various reasons)
        order = gateway.create_order("BTC/USDT", "market", "buy", 1000000)  # Very large amount
        print(f"✅ Order placed: {order['id']}")
    except InsufficientFunds as e:
        print(f"❌ Insufficient funds: {e}")
    except BadSymbol as e:
        print(f"❌ Bad symbol: {e}")
    except OrderNotFound as e:
        print(f"❌ Order not found: {e}")
    except ExchangeError as e:
        print(f"❌ Exchange error: {e}")
    except Exception as e:
        print(f"⚠️  Unexpected trading error: {e}")

    # 5. Handle authentication errors
    print("\n5. Authentication Error Handling:")
    try:
        # Try with invalid API key
        bad_gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="invalid-key")
        balance = bad_gateway.fetch_balance()
        print(f"✅ Balance fetched: {balance}")
    except AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        print("   Check your API key")
    except Exception as e:
        print(f"⚠️  Unexpected auth error: {e}")


def demonstrate_graceful_degradation():
    """Demonstrate graceful degradation when features aren't available."""
    print("\n=== Graceful Degradation Example ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Example: Try to get market data, fallback to basic info if advanced features unavailable
    symbol = "BTC/USDT"

    print(f"Getting market data for {symbol}:")

    # Try to get comprehensive market data
    market_data = {}

    # Basic ticker (usually available)
    if gateway.has.get("fetchTicker", False):
        try:
            ticker = gateway.fetch_ticker(symbol)
            market_data["ticker"] = ticker
            print(f"✅ Ticker: ${ticker.get('last', 'N/A')}")
        except Exception as e:
            print(f"❌ Ticker failed: {e}")
    else:
        print("❌ Ticker not supported")

    # OHLCV data (might not be available in paper mode)
    if gateway.has.get("fetchOHLCV", False):
        try:
            ohlcv = gateway.fetch_ohlcv(symbol, "1h", limit=24)
            market_data["ohlcv"] = ohlcv
            print(f"✅ OHLCV: {len(ohlcv)} candles")
        except Exception as e:
            print(f"❌ OHLCV failed: {e}")
    else:
        print("❌ OHLCV not supported (paper mode limitation)")

    # Order book (might not be available in paper mode)
    if gateway.has.get("fetchOrderBook", False):
        try:
            orderbook = gateway.fetch_order_book(symbol)
            market_data["orderbook"] = orderbook
            print(f"✅ Order book: {len(orderbook['bids'])} bids, {len(orderbook['asks'])} asks")
        except Exception as e:
            print(f"❌ Order book failed: {e}")
    else:
        print("❌ Order book not supported (paper mode limitation)")

    print(f"\n📊 Market data summary: {len(market_data)} data sources available")


def demonstrate_error_recovery():
    """Demonstrate error recovery patterns."""
    print("\n=== Error Recovery Example ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Example: Retry pattern for network operations
    def retry_operation(operation, max_retries=3, delay=1):
        """Retry an operation with exponential backoff."""
        import time

        for attempt in range(max_retries):
            try:
                return operation()
            except NetworkError as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Network error (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"   Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"❌ Failed after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                print(f"❌ Non-retryable error: {e}")
                raise

    # Try to load markets with retry
    try:
        markets = retry_operation(lambda: gateway.load_markets())
        print(f"✅ Markets loaded successfully: {len(markets)} pairs")
    except Exception as e:
        print(f"❌ Failed to load markets: {e}")


if __name__ == "__main__":
    demonstrate_error_handling()
    demonstrate_graceful_degradation()
    demonstrate_error_recovery()

    print("\n🎯 Error Handling Summary:")
    print("✅ Always check gateway.has before using features")
    print("✅ Use specific exception types for different errors")
    print("✅ Implement graceful degradation for missing features")
    print("✅ Use retry patterns for network operations")
    print("✅ Provide helpful error messages to users")
