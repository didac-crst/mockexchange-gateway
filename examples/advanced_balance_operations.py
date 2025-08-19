"""examples/advanced_balance_operations.py

Advanced balance operations example for MockX Gateway.

This example demonstrates the new balance operations and MockExchange-specific
features that extend beyond standard CCXT functionality.
"""

from mockexchange_gateway import create_paper_gateway


def demonstrate_balance_operations():
    """Demonstrate advanced balance operations."""
    print("=== Advanced Balance Operations Example ===")

    # Create gateway
    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        # 1. Fetch full balance (CCXT standard)
        print("\n1. Fetch Full Balance (CCXT Standard):")
        balance = gateway.fetch_balance()
        print(f"✅ Full balance fetched: {len(balance.get('free', {}))} assets")

        # Show some balance details
        free_balances = balance.get("free", {})
        for asset, amount in list(free_balances.items())[:3]:  # Show first 3
            if amount > 0:
                print(f"   {asset}: {amount}")

        # 2. Fetch balance list (MockExchange-specific)
        print("\n2. Fetch Balance List (MockExchange-Specific):")
        if gateway.has.get("fetchBalanceList", False):
            balance_list = gateway.fetch_balance_list()
            print(f"✅ Balance list fetched: {balance_list.get('length', 0)} assets")
            print(f"   Assets: {balance_list.get('assets', [])[:5]}...")  # Show first 5
        else:
            print("❌ Balance list not supported")

        # 3. Fetch specific asset balance (CCXT standard)
        print("\n3. Fetch Specific Asset Balance (CCXT Standard):")
        try:
            usdt_balance = gateway.fetch_balance("USDT")
            print(f"✅ USDT balance: {usdt_balance}")
        except Exception as e:
            print(f"❌ Error fetching USDT balance: {e}")

        # 4. Deposit funds (MockExchange-specific)
        print("\n4. Deposit Funds (MockExchange-Specific):")
        try:
            deposit_result = gateway.deposit("USDT", 1000.0)
            print(f"✅ Deposited 1000 USDT: {deposit_result}")

            # Check balance after deposit
            new_balance = gateway.fetch_balance("USDT")
            print(f"   New USDT balance: {new_balance}")
        except Exception as e:
            print(f"❌ Error depositing funds: {e}")

        # 5. Withdraw funds (MockExchange-specific)
        print("\n5. Withdraw Funds (MockExchange-Specific):")
        try:
            withdraw_result = gateway.withdraw("USDT", 100.0)
            print(f"✅ Withdrew 100 USDT: {withdraw_result}")

            # Check balance after withdrawal
            final_balance = gateway.fetch_balance("USDT")
            print(f"   Final USDT balance: {final_balance}")
        except Exception as e:
            print(f"❌ Error withdrawing funds: {e}")

        # 6. Check order execution (MockExchange-specific)
        print("\n6. Check Order Execution (MockExchange-Specific):")
        try:
            can_execute = gateway.can_execute_order(
                symbol="BTC/USDT", type="market", side="buy", amount=0.001
            )
            print(f"✅ Can execute order check: {can_execute}")
        except Exception as e:
            print(f"❌ Error checking order execution: {e}")

    except Exception as e:
        print(f"❌ General error: {e}")


def demonstrate_balance_comparison():
    """Demonstrate different balance fetching methods."""
    print("\n=== Balance Method Comparison ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    try:
        # Method 1: Full balance (CCXT standard)
        print("\nMethod 1: Full Balance (fetch_balance())")
        full_balance = gateway.fetch_balance()
        print(f"   Type: {type(full_balance)}")
        print(f"   Keys: {list(full_balance.keys())}")
        print(f"   Free assets: {len(full_balance.get('free', {}))}")

        # Method 2: Balance list (MockExchange-specific)
        print("\nMethod 2: Balance List (fetch_balance_list())")
        if gateway.has.get("fetchBalanceList", False):
            balance_list = gateway.fetch_balance_list()
            print(f"   Type: {type(balance_list)}")
            print(f"   Keys: {list(balance_list.keys())}")
            print(f"   Asset count: {balance_list.get('length', 0)}")
        else:
            print("   ❌ Not supported")

        # Method 3: Specific asset (CCXT standard)
        print("\nMethod 3: Specific Asset (fetch_balance('USDT'))")
        try:
            usdt_balance = gateway.fetch_balance("USDT")
            print(f"   Type: {type(usdt_balance)}")
            print(f"   Keys: {list(usdt_balance.keys())}")
            print(f"   USDT free: {usdt_balance.get('free', {}).get('USDT', 0)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Error in comparison: {e}")


def demonstrate_capability_checking():
    """Demonstrate capability checking for new features."""
    print("\n=== Capability Checking for New Features ===")

    gateway = create_paper_gateway(base_url="http://localhost:8000", api_key="dev-key")

    # Check capabilities for new features
    new_features = [
        "fetchBalanceList",
        "deposit",
        "withdraw",
        "canExecuteOrder",
    ]

    print("New feature capabilities:")
    for feature in new_features:
        is_supported = gateway.has.get(feature, False)
        status = "✅" if is_supported else "❌"
        print(f"  {status} {feature}")

    # Show how to use capability checking
    print("\nUsing capability checking:")
    if gateway.has.get("fetchBalanceList", False):
        print("  ✅ Balance list is supported - using it")
        balance_list = gateway.fetch_balance_list()
        print(f"     Result: {balance_list}")
    else:
        print("  ❌ Balance list not supported - using fallback")
        full_balance = gateway.fetch_balance()
        print(f"     Fallback: {len(full_balance.get('free', {}))} assets")


if __name__ == "__main__":
    demonstrate_balance_operations()
    demonstrate_balance_comparison()
    demonstrate_capability_checking()

    print("\n🎯 Advanced Balance Operations Summary:")
    print("✅ fetch_balance() - CCXT standard (full or specific asset)")
    print("✅ fetch_balance_list() - MockExchange-specific balance list")
    print("✅ deposit() - MockExchange-specific funding")
    print("✅ withdraw() - MockExchange-specific withdrawals")
    print("✅ can_execute_order() - MockExchange-specific dry run")
    print("✅ Always check gateway.has before using features")
    print("✅ MockExchange-specific features extend beyond CCXT")
