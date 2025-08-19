"""Integration tests for paper mode (MockExchange).

These tests make real HTTP calls to a MockExchange instance and verify
that the gateway correctly handles the responses.
"""

import pytest

from tests.helpers.credentials import skip_if_no_credentials


@pytest.mark.integration
@pytest.mark.paper
@skip_if_no_credentials()
class TestPaperModeIntegration:
    """Integration tests for paper mode functionality."""

    def test_load_markets(self, integration_paper_gateway):
        """Test loading markets from MockExchange."""
        gateway = integration_paper_gateway

        markets = gateway.load_markets()

        # Basic assertions about market structure
        assert isinstance(markets, dict)
        assert len(markets) > 0

        # Check that we have some common trading pairs
        # (MockExchange should provide these)
        common_pairs = ["BTC/USDT", "ETH/USDT"]
        found_pairs = [pair for pair in common_pairs if pair in markets]
        assert len(found_pairs) > 0, f"No common pairs found. Available: {list(markets.keys())[:5]}"

    def test_fetch_ticker(self, integration_paper_gateway, test_symbol):
        """Test fetching ticker data from MockExchange."""
        gateway = integration_paper_gateway

        # Load markets first
        gateway.load_markets()

        ticker = gateway.fetch_ticker(test_symbol)

        # Verify CCXT-compatible ticker structure
        required_fields = ["symbol", "timestamp", "datetime", "last", "bid", "ask"]
        for field in required_fields:
            assert field in ticker, f"Missing required field: {field}"

        # Verify data types and reasonable values
        assert ticker["symbol"] == test_symbol
        assert isinstance(ticker["timestamp"], (int, float, type(None)))  # Allow float timestamps
        assert isinstance(ticker["last"], (float, int, type(None)))
        assert isinstance(ticker["bid"], (float, int, type(None)))
        assert isinstance(ticker["ask"], (float, int, type(None)))

    def test_fetch_balance(self, integration_paper_gateway):
        """Test fetching account balance from MockExchange."""
        gateway = integration_paper_gateway

        balance = gateway.fetch_balance()

        # Verify CCXT-compatible balance structure
        assert isinstance(balance, dict)

        # Should have standard CCXT balance fields
        expected_fields = ["info", "timestamp", "datetime", "free", "used", "total"]
        for field in expected_fields:
            assert field in balance, f"Missing balance field: {field}"

        # Free, used, total should be dicts with currency symbols as keys
        for field in ["free", "used", "total"]:
            assert isinstance(balance[field], dict)

    def test_gateway_capabilities(self, integration_paper_gateway):
        """Test that gateway reports correct capabilities for paper mode."""
        gateway = integration_paper_gateway

        # Check that has dict is populated
        assert isinstance(gateway.has, dict)
        assert len(gateway.has) > 0

        # Paper mode should support basic trading operations
        expected_supported = [
            "fetchTicker",
            "fetchBalance",
            "loadMarkets",
            "createOrder",
            "cancelOrder",
            "fetchOpenOrders",
        ]

        for feature in expected_supported:
            assert feature in gateway.has, f"Missing capability: {feature}"
            # Check that it's actually supported (True) or explicitly not supported (False)
            assert gateway.has[feature] in [
                True,
                False,
            ], f"Capability {feature} should be True or False"

        # Paper mode should NOT support these features
        expected_not_supported = ["fetchOHLCV", "fetchOrderBook", "fetchTrades"]

        for feature in expected_not_supported:
            if feature in gateway.has:
                assert (
                    gateway.has[feature] is False
                ), f"Feature {feature} should not be supported in paper mode"

    def test_unsupported_method_raises_error(self, integration_paper_gateway, test_symbol):
        """Test that unsupported methods raise NotSupported errors."""
        gateway = integration_paper_gateway

        from mockexchange_gateway import NotSupported

        # Load markets first
        gateway.load_markets()

        # These methods should raise NotSupported in paper mode
        with pytest.raises(NotSupported) as exc_info:
            gateway.fetch_ohlcv(test_symbol, "1h")

        assert "fetch_ohlcv" in str(exc_info.value).lower()
        assert "paper" in str(exc_info.value).lower()

    def test_create_order_basic(self, integration_paper_gateway, test_symbol, test_amount):
        """Test creating a basic market order."""
        gateway = integration_paper_gateway

        # Load markets first
        gateway.load_markets()

        # Create a small market buy order
        order = gateway.create_order(
            symbol=test_symbol, type="market", side="buy", amount=test_amount
        )

        # Verify CCXT-compatible order structure
        required_fields = ["id", "symbol", "type", "side", "amount", "status"]
        for field in required_fields:
            assert field in order, f"Missing order field: {field}"

        # Verify order details
        assert order["symbol"] == test_symbol
        assert order["type"] == "market"
        assert order["side"] == "buy"
        assert order["amount"] == test_amount
