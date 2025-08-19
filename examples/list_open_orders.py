"""examples/list_open_orders.py

Example: listing open orders from MockExchange.

This example demonstrates how to:
1. Create a gateway instance
2. Load markets
3. Fetch open orders
4. Display order information
"""

from mockexchange_gateway import create_paper_gateway


def main():
    """Main function demonstrating open orders listing."""
    print("=== Listing Open Orders Example ===")

    # Create gateway
    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        # Load markets first
        markets = gateway.load_markets()
        print(f"Loaded {len(markets)} markets")

        # Fetch open orders
        open_orders = gateway.fetch_open_orders()
        print(f"Found {len(open_orders)} open orders")

        # Display order details
        for order in open_orders:
            print(
                f"Order {order['id']}: {order['symbol']} {order['side']} {order['amount']} @ {order.get('price', 'market')}"
            )

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MockExchange is running at http://localhost:8000")


if __name__ == "__main__":
    main()
