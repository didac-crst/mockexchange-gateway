"""examples/debug_orders.py

Debug script to test orders endpoint directly.
"""

import requests

from mockexchange_gateway import create_paper_gateway


def debug_orders():
    """Debug orders endpoint."""
    print("=== Debugging Orders Endpoint ===")

    # Test direct HTTP request first
    print("\n1. Testing direct HTTP request...")
    try:
        response = requests.get(
            "http://localhost:8000/orders",
            headers={"x-api-key": "dev-key", "Content-Type": "application/json"},
            params={"status": "open"},
        )
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")

        if response.status_code == 200:
            data = response.json()
            print(f"   Data type: {type(data)}")
            print(f"   Data length: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   Error response: {response.text}")

    except Exception as e:
        print(f"   ❌ Direct request failed: {e}")

    # Test through gateway
    print("\n2. Testing through gateway...")
    try:
        gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

        # Test fetch_orders without status filter
        print("   Testing fetch_orders()...")
        orders = gateway.fetch_orders()
        print(f"   ✅ fetch_orders() returned {len(orders)} orders")

        # Test fetch_open_orders
        print("   Testing fetch_open_orders()...")
        open_orders = gateway.fetch_open_orders()
        print(f"   ✅ fetch_open_orders() returned {len(open_orders)} orders")

    except Exception as e:
        print(f"   ❌ Gateway request failed: {e}")
        print(f"   Error type: {type(e).__name__}")


if __name__ == "__main__":
    debug_orders()
