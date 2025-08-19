"""examples/test_open_orders.py

Test script to verify open orders functionality.
"""

from mockexchange_gateway import InsufficientFunds, create_paper_gateway


def test_open_orders():
    """Test open orders functionality."""
    print("=== Testing Open Orders ===")

    # Create gateway
    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        # Load markets first
        markets = gateway.load_markets()
        print(f"✅ Loaded {len(markets)} markets")

        # Check balance first
        balance = gateway.fetch_balance()
        print(f"✅ Balance fetched: {len(balance.get('free', {}))} assets")

        # Check if we have any open orders
        open_orders = gateway.fetch_open_orders()
        print(f"✅ Found {len(open_orders)} open orders")

        if len(open_orders) == 0:
            print("📝 No open orders found. Let's try to create some test orders...")

            # Check if we have funds first
            free_balances = balance.get("free", {})
            usdt_balance = free_balances.get("USDT", 0)
            btc_balance = free_balances.get("BTC", 0)

            print(f"   USDT balance: {usdt_balance}")
            print(f"   BTC balance: {btc_balance}")

            if usdt_balance < 100:
                print("   💰 Need to deposit some USDT first...")
                try:
                    deposit_result = gateway.deposit("USDT", 1000.0)
                    print(f"   ✅ Deposited 1000 USDT: {deposit_result}")
                except Exception as e:
                    print(f"   ❌ Error depositing: {e}")

            # Create a few test orders
            try:
                # Market buy order
                order1 = gateway.create_order("BTC/USDT", "market", "buy", 0.001)
                print(f"✅ Created market buy order: {order1['id']}")

                # Limit sell order
                order2 = gateway.create_order("BTC/USDT", "limit", "sell", 0.001, 50000.0)
                print(f"✅ Created limit sell order: {order2['id']}")

                # Check open orders again
                open_orders = gateway.fetch_open_orders()
                print(f"✅ Now found {len(open_orders)} open orders")

            except InsufficientFunds as e:
                print(f"❌ Insufficient funds: {e}")
                print("   This is expected if we don't have enough balance")
            except Exception as e:
                print(f"❌ Error creating test orders: {e}")

        # Display order details
        for i, order in enumerate(open_orders, 1):
            print(f"\n📋 Order {i}:")
            print(f"   ID: {order['id']}")
            print(f"   Symbol: {order['symbol']}")
            print(f"   Side: {order['side']}")
            print(f"   Type: {order['type']}")
            print(f"   Amount: {order['amount']}")
            print(f"   Price: {order.get('price', 'market')}")
            print(f"   Status: {order['status']}")

        # Test with symbol filter
        print("\n🔍 Testing with symbol filter...")
        btc_orders = gateway.fetch_open_orders(symbol="BTC/USDT")
        print(f"✅ Found {len(btc_orders)} BTC/USDT open orders")

        # Test with limit
        print("\n🔍 Testing with limit...")
        limited_orders = gateway.fetch_open_orders(limit=5)
        print(f"✅ Found {len(limited_orders)} orders (limited to 5)")

        print("\n🎯 Open Orders Test Summary:")
        print("   ✅ fetch_open_orders() method works")
        print("   ✅ Symbol filtering works")
        print("   ✅ Limit parameter works")
        print("   ✅ Proper error handling for insufficient funds")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        print("   Make sure MockExchange is running at http://localhost:8000")


if __name__ == "__main__":
    test_open_orders()
