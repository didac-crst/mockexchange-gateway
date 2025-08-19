"""examples/fetch_ticker.py

Ticker fetching example for MockX Gateway.

This example demonstrates how to fetch real-time ticker data
for trading pairs, showing the CCXT-compatible data structure.
"""

from mockexchange_gateway import NotSupported, create_paper_gateway


def demonstrate_ticker_fetching():
    """Demonstrate fetching ticker data for various symbols."""
    print("=== Ticker Fetching Example ===")

    # Create gateway
    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Common trading pairs to test
    symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]

    print(f"Fetching tickers for {len(symbols)} symbols...")

    for symbol in symbols:
        try:
            # Fetch ticker data
            ticker = gateway.fetch_ticker(symbol)

            print(f"\n📊 {symbol} Ticker:")
            print(f"  Last Price: ${ticker.get('last', 'N/A')}")
            print(f"  Bid: ${ticker.get('bid', 'N/A')}")
            print(f"  Ask: ${ticker.get('ask', 'N/A')}")
            print(f"  High: ${ticker.get('high', 'N/A')}")
            print(f"  Low: ${ticker.get('low', 'N/A')}")
            print(f"  Volume: {ticker.get('baseVolume', 'N/A')} {symbol.split('/')[0]}")
            print(f"  Quote Volume: {ticker.get('quoteVolume', 'N/A')} {symbol.split('/')[1]}")
            print(f"  Timestamp: {ticker.get('timestamp', 'N/A')}")

            # Calculate spread if bid/ask available
            if ticker.get("bid") and ticker.get("ask"):
                spread = ticker["ask"] - ticker["bid"]
                spread_percent = (spread / ticker["bid"]) * 100
                print(f"  Spread: ${spread:.4f} ({spread_percent:.2f}%)")

        except NotSupported as e:
            print(f"❌ {symbol}: {e}")
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")


def demonstrate_ticker_structure():
    """Demonstrate the CCXT-compatible ticker data structure."""
    print("\n=== Ticker Data Structure ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        ticker = gateway.fetch_ticker("BTC/USDT")

        print("📋 CCXT-Compatible Ticker Structure:")
        print("=" * 40)

        # Show all available fields
        for key, value in ticker.items():
            if key == "info":
                print(f"  {key}: <exchange-specific data>")
            else:
                print(f"  {key}: {value}")

        print("\n📊 Key Metrics:")
        print(f"  Symbol: {ticker.get('symbol')}")
        print(f"  Last Price: ${ticker.get('last')}")
        print(f"  Bid/Ask Spread: ${ticker.get('ask', 0) - ticker.get('bid', 0):.2f}")
        print(f"  24h High: ${ticker.get('high')}")
        print(f"  24h Low: ${ticker.get('low')}")
        print(f"  Volume: {ticker.get('baseVolume')} {ticker.get('symbol', '').split('/')[0]}")

    except Exception as e:
        print(f"❌ Error fetching ticker structure: {e}")


def demonstrate_multiple_tickers():
    """Demonstrate fetching multiple tickers at once."""
    print("\n=== Multiple Tickers Example ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Check if fetchTickers is supported
    if not gateway.has.get("fetchTickers", False):
        print("❌ fetchTickers not supported in this mode")
        print("   Fetching individual tickers instead...")

        # Fallback to individual tickers
        symbols = ["BTC/USDT", "ETH/USDT"]
        tickers = {}

        for symbol in symbols:
            try:
                tickers[symbol] = gateway.fetch_ticker(symbol)
            except Exception as e:
                print(f"❌ Failed to fetch {symbol}: {e}")
    else:
        try:
            # Fetch all tickers at once
            tickers = gateway.fetch_tickers()
            print(f"✅ Fetched {len(tickers)} tickers")
        except Exception as e:
            print(f"❌ Error fetching tickers: {e}")
            return

    # Display summary
    print(f"\n📊 Ticker Summary ({len(tickers)} symbols):")
    print("-" * 50)

    for symbol, ticker in tickers.items():
        last_price = ticker.get("last", "N/A")
        volume = ticker.get("baseVolume", "N/A")
        print(f"  {symbol}: ${last_price} (Vol: {volume})")


def demonstrate_ticker_analysis():
    """Demonstrate basic ticker analysis."""
    print("\n=== Ticker Analysis Example ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        ticker = gateway.fetch_ticker("BTC/USDT")

        # Basic analysis
        last_price = ticker.get("last", 0)
        high_24h = ticker.get("high", 0)
        low_24h = ticker.get("low", 0)
        volume_24h = ticker.get("baseVolume", 0)

        if last_price and high_24h and low_24h:
            # Calculate price position within 24h range
            price_range = high_24h - low_24h
            if price_range > 0:
                price_position = (last_price - low_24h) / price_range
                print("📈 Price Analysis:")
                print(f"  24h Range: ${low_24h:.2f} - ${high_24h:.2f}")
                print(f"  Current Position: {price_position:.1%} of range")
                print(f"  24h Volume: {volume_24h:.2f} BTC")

                # Simple trend indicator
                if price_position > 0.7:
                    print("  📈 Trend: Near 24h high")
                elif price_position < 0.3:
                    print("  📉 Trend: Near 24h low")
                else:
                    print("  ➡️  Trend: Mid-range")

        # Spread analysis
        bid = ticker.get("bid", 0)
        ask = ticker.get("ask", 0)
        if bid and ask:
            spread = ask - bid
            spread_percent = (spread / bid) * 100
            print("\n💱 Spread Analysis:")
            print(f"  Bid: ${bid:.2f}")
            print(f"  Ask: ${ask:.2f}")
            print(f"  Spread: ${spread:.2f} ({spread_percent:.3f}%)")

            # Spread quality indicator
            if spread_percent < 0.1:
                print("  ✅ Excellent liquidity (tight spread)")
            elif spread_percent < 0.5:
                print("  ✅ Good liquidity")
            else:
                print("  ⚠️  Wide spread (low liquidity)")

    except Exception as e:
        print(f"❌ Error in ticker analysis: {e}")


if __name__ == "__main__":
    demonstrate_ticker_fetching()
    demonstrate_ticker_structure()
    demonstrate_multiple_tickers()
    demonstrate_ticker_analysis()

    print("\n🎯 Ticker Fetching Summary:")
    print("✅ Use fetch_ticker(symbol) for individual symbols")
    print("✅ Use fetch_tickers() for multiple symbols (if supported)")
    print("✅ Check gateway.has['fetchTicker'] before using")
    print("✅ Handle NotSupported errors gracefully")
    print("✅ Ticker data follows CCXT structure for compatibility")
