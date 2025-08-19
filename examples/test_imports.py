"""examples/test_imports.py

Simple import test to verify the MockX Gateway is working correctly.
This example doesn't require MockExchange to be running.
"""

from mockexchange_gateway import ExchangeFactory, NotSupported


def test_imports():
    """Test that all imports work correctly."""
    print("✅ All imports successful!")

    # Test gateway creation (without making network calls)
    try:
        # Test with explicit configuration (library best practice)
        gateway = ExchangeFactory.create_paper_gateway(
            base_url="http://localhost:8000", api_key="test-key"
        )
        print(f"✅ Paper gateway created: {gateway}")
        print(f"✅ Gateway capabilities: {len(gateway.has)} features")

        # Test factory class method
        gateway2 = ExchangeFactory.create_paper_gateway(
            base_url="http://localhost:8000", api_key="test-key-2"
        )
        print(f"✅ Factory method works: {gateway2}")

        # Test capabilities
        print(f"✅ Has createOrder: {gateway.has.get('createOrder', False)}")
        print(f"✅ Has fetchOHLCV: {gateway.has.get('fetchOHLCV', False)}")

        # Test error handling
        try:
            gateway.fetch_ohlcv("BTC/USDT", "1h")
        except NotSupported as e:
            print(f"✅ Correctly raised NotSupported: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 MockX Gateway Import Test")
    print("=" * 40)

    success = test_imports()

    if success:
        print("\n🎉 All tests passed! MockX Gateway is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
