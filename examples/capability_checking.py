"""examples/capability_checking.py

Capability checking example for MockX Gateway.

This example demonstrates how to check what features are available
before using them, enabling graceful degradation and better error handling.
"""

from mockexchange_gateway import create_paper_gateway


def demonstrate_capability_checking():
    """Demonstrate how to check capabilities before using features."""
    print("=== Capability Checking Example ===")

    # Create gateways for both modes
    paper_gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    print("📊 Paper Mode Capabilities:")
    check_capabilities(paper_gateway, "Paper")

    # Note: Production gateway creation is commented out as it requires real API keys
    # prod_gateway = create_prod_gateway(
    #     exchange_id="binance",
    #     api_key="your-api-key",
    #     secret="your-secret",
    #     sandbox=True
    # )
    # print("\n📊 Production Mode Capabilities:")
    # check_capabilities(prod_gateway, "Production")


def check_capabilities(gateway, mode_name):
    """Check and display gateway capabilities."""

    # Define feature categories
    categories = {
        "Core Trading": [
            "createOrder",
            "cancelOrder",
            "fetchOrder",
            "fetchOrders",
            "fetchOpenOrders",
            "fetchClosedOrders",
        ],
        "Account & Balance": [
            "fetchBalance",
            "fetchPositions",
            "fetchLedger",
        ],
        "Market Data": [
            "fetchTicker",
            "fetchTickers",
            "fetchOHLCV",
            "fetchOrderBook",
            "fetchTrades",
        ],
        "Metadata": [
            "loadMarkets",
            "fetchMarkets",
        ],
        "Advanced Features": [
            "fetchLeverage",
            "setLeverage",
            "fetchFundingRate",
            "fetchFundingHistory",
        ],
    }

    print(f"\n{mode_name} Mode Gateway Capabilities:")
    print("=" * 50)

    for category, features in categories.items():
        print(f"\n{category}:")
        for feature in features:
            is_supported = gateway.has.get(feature, False)
            status = "✅" if is_supported else "❌"
            print(f"  {status} {feature}")

    # Show summary
    total_features = sum(len(features) for features in categories.values())
    supported_features = sum(
        1
        for features in categories.values()
        for feature in features
        if gateway.has.get(feature, False)
    )

    print(f"\n📈 Summary: {supported_features}/{total_features} features supported")


def demonstrate_safe_feature_usage():
    """Demonstrate safe usage patterns based on capabilities."""
    print("\n=== Safe Feature Usage Example ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Example 1: Safe market data fetching
    print("\n1. Safe Market Data Fetching:")
    symbol = "BTC/USDT"

    # Always check before using
    if gateway.has.get("fetchTicker", False):
        try:
            ticker = gateway.fetch_ticker(symbol)
            print(f"✅ Ticker: ${ticker.get('last', 'N/A')}")
        except Exception as e:
            print(f"❌ Ticker failed: {e}")
    else:
        print("❌ Ticker not supported in this mode")

    # Example 2: Safe OHLCV fetching
    if gateway.has.get("fetchOHLCV", False):
        try:
            ohlcv = gateway.fetch_ohlcv(symbol, "1h", limit=24)
            print(f"✅ OHLCV: {len(ohlcv)} candles")
        except Exception as e:
            print(f"❌ OHLCV failed: {e}")
    else:
        print("❌ OHLCV not supported in this mode")

    # Example 3: Safe order book fetching
    if gateway.has.get("fetchOrderBook", False):
        try:
            orderbook = gateway.fetch_order_book(symbol)
            print(f"✅ Order book: {len(orderbook['bids'])} bids, {len(orderbook['asks'])} asks")
        except Exception as e:
            print(f"❌ Order book failed: {e}")
    else:
        print("❌ Order book not supported in this mode")

    # Example 4: Safe trading operations
    print("\n2. Safe Trading Operations:")

    if gateway.has.get("createOrder", False):
        try:
            # Use a very small amount for testing
            order = gateway.create_order(symbol, "market", "buy", 0.001)
            print(f"✅ Order created: {order['id']}")

            # Check if we can cancel orders
            if gateway.has.get("cancelOrder", False):
                try:
                    cancelled = gateway.cancel_order(order["id"], symbol)
                    print(f"✅ Order cancelled: {cancelled['id']}")
                except Exception as e:
                    print(f"❌ Cancel failed: {e}")
            else:
                print("❌ Cancel order not supported")

        except Exception as e:
            print(f"❌ Order creation failed: {e}")
    else:
        print("❌ Order creation not supported")


def demonstrate_feature_detection():
    """Demonstrate advanced feature detection patterns."""
    print("\n=== Advanced Feature Detection ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Example: Detect what type of trading is supported
    print("\nTrading Feature Detection:")

    trading_features = {
        "spot_trading": gateway.has.get("createOrder", False)
        and gateway.has.get("fetchBalance", False),
        "futures_trading": gateway.has.get("fetchPositions", False),
        "margin_trading": gateway.has.get("fetchLeverage", False),
        "market_data": gateway.has.get("fetchTicker", False),
        "advanced_data": gateway.has.get("fetchOHLCV", False)
        and gateway.has.get("fetchOrderBook", False),
    }

    for feature, is_supported in trading_features.items():
        status = "✅" if is_supported else "❌"
        print(f"  {status} {feature.replace('_', ' ').title()}")

    # Example: Determine best available data source
    print("\nBest Available Data Source:")

    if gateway.has.get("fetchOHLCV", False):
        print("  ✅ OHLCV data available (best for analysis)")
    elif gateway.has.get("fetchOrderBook", False):
        print("  ✅ Order book available (good for depth analysis)")
    elif gateway.has.get("fetchTicker", False):
        print("  ✅ Ticker available (basic price info)")
    else:
        print("  ❌ No market data available")

    # Example: Check order type support
    print("\nOrder Type Support:")

    order_types = {
        "market_orders": gateway.has.get("createOrder", False),
        "limit_orders": gateway.has.get("createOrder", False),  # Most exchanges support this
        "stop_orders": gateway.has.get("createStopOrder", False),
        "stop_limit_orders": gateway.has.get("createStopLimitOrder", False),
    }

    for order_type, is_supported in order_types.items():
        status = "✅" if is_supported else "❌"
        print(f"  {status} {order_type.replace('_', ' ').title()}")


def demonstrate_conditional_workflows():
    """Demonstrate conditional workflows based on capabilities."""
    print("\n=== Conditional Workflows ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Example: Adaptive trading strategy based on available features
    print("\nAdaptive Trading Strategy:")

    strategy_features = []

    # Check what we can do
    if gateway.has.get("fetchTicker", False):
        strategy_features.append("price_monitoring")

    if gateway.has.get("fetchOHLCV", False):
        strategy_features.append("technical_analysis")

    if gateway.has.get("fetchOrderBook", False):
        strategy_features.append("order_book_analysis")

    if gateway.has.get("createOrder", False):
        strategy_features.append("automated_trading")

    if gateway.has.get("fetchBalance", False):
        strategy_features.append("position_tracking")

    print(f"Available strategy features: {', '.join(strategy_features)}")

    # Determine strategy type
    if "automated_trading" in strategy_features and "price_monitoring" in strategy_features:
        if "technical_analysis" in strategy_features:
            print("  🚀 Full automated trading strategy possible")
        else:
            print("  📊 Basic automated trading strategy possible")
    elif "price_monitoring" in strategy_features:
        print("  👀 Monitoring-only strategy possible")
    else:
        print("  ❌ No trading strategy possible with available features")


if __name__ == "__main__":
    demonstrate_capability_checking()
    demonstrate_safe_feature_usage()
    demonstrate_feature_detection()
    demonstrate_conditional_workflows()

    print("\n🎯 Capability Checking Best Practices:")
    print("✅ Always check gateway.has before using features")
    print("✅ Implement graceful degradation for missing features")
    print("✅ Use conditional workflows based on available capabilities")
    print("✅ Provide clear feedback about what's supported")
    print("✅ Design strategies that adapt to available features")
