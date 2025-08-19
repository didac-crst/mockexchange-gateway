"""examples/place_market_order.py

Example: placing a market order.

This example demonstrates how to:
1. Create a gateway instance
2. Load markets
3. Place a market order
4. Display order information
"""

from mockexchange_gateway import create_paper_gateway


def main():
    """Main function demonstrating market order placement."""
    print("=== Placing Market Order Example ===")

    # Create gateway
    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        # Load markets first
        markets = gateway.load_markets()
        print(f"Loaded {len(markets)} markets")

        # Place a market buy order for 0.001 BTC
        order = gateway.create_order("BTC/USDT", "market", "buy", 0.001)
        print("Order placed successfully!")
        print(f"Order ID: {order['id']}")
        print(f"Symbol: {order['symbol']}")
        print(f"Type: {order['type']}")
        print(f"Side: {order['side']}")
        print(f"Amount: {order['amount']}")
        print(f"Status: {order['status']}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MockExchange is running at http://localhost:8000")


if __name__ == "__main__":
    main()
