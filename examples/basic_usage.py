"""examples/basic_usage.py

Demonstrates both paper and production mode configuration.

This example shows how to create gateways with explicit configuration,
which is the recommended approach for libraries.
"""

from mockexchange_gateway import ExchangeFactory


def paper_mode_example():
    """Example using paper mode (MockExchange)."""
    print("=== Paper Mode Example ===")

    # Create paper mode gateway with explicit configuration
    gateway = ExchangeFactory.create_paper_gateway(
        base_url="http://localhost:8000", api_key="dev-key"
    )

    print("Gateway mode: Paper")
    print(f"Gateway capabilities: {len(gateway.has)} features")
    print(f"Supports createOrder: {gateway.has.get('createOrder', False)}")
    print(f"Supports fetchOHLCV: {gateway.has.get('fetchOHLCV', False)}")

    try:
        # Load markets
        markets = gateway.load_markets()
        print(f"Markets loaded: {len(markets)} trading pairs")

        # Fetch balance
        balance = gateway.fetch_balance()
        print(f"Balance structure: {list(balance.keys())}")

    except Exception as e:
        print(f"Error (expected if MockExchange not running): {e}")


def production_mode_example():
    """Example using production mode (CCXT) - requires API keys."""
    print("\n=== Production Mode Example ===")

    # This would create a production gateway (commented out as it requires real API keys)
    """
    gateway = ExchangeFactory.create_prod_gateway(
        exchange_id="binance",  # or 'coinbase', 'kraken', etc.
        api_key="your-exchange-api-key",
        secret="your-exchange-secret",
        sandbox=True  # Use testnet for safety
    )
    """

    print("Production mode requires valid API credentials.")
    print("Uncomment the code above and add your exchange API keys to test.")
    print("Supported exchanges: binance, coinbase, kraken, and many more via CCXT.")


def factory_class_example():
    """Example using the factory class directly."""
    print("\n=== Factory Class Example ===")

    # Using factory class directly
    gateway = ExchangeFactory.create_paper_gateway(
        base_url="http://localhost:8000", api_key="factory-test-key"
    )

    print(f"Factory-created gateway: {gateway}")
    print("Clean, professional API")

    # Example of production gateway creation (commented out)
    """
    prod_gateway = ExchangeFactory.create_prod_gateway(
        exchange_id="coinbase",  # or 'binance', 'kraken', etc.
        api_key="your-exchange-key",
        secret="your-exchange-secret"
    )
    """


if __name__ == "__main__":
    paper_mode_example()
    production_mode_example()
    factory_class_example()
