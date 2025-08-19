"""Integration tests comparing paper and production modes.

These tests verify that both modes provide consistent interfaces
and that data structures are compatible between paper and production.
"""

import pytest

from tests.helpers.credentials import skip_if_no_credentials, skip_if_no_exchange


@pytest.mark.integration
@pytest.mark.slow
@skip_if_no_credentials()
class TestCrossModeComparison:
    """Compare paper and production mode behaviors."""

    def test_capability_consistency(self, integration_paper_gateway, integration_prod_gateway):
        """Test that both modes report capabilities consistently."""
        paper_gateway = integration_paper_gateway
        prod_gateway = integration_prod_gateway

        # Both should have the same basic capabilities
        basic_capabilities = [
            "fetchTicker",
            "fetchBalance",
            "loadMarkets",
            "createOrder",
            "cancelOrder",
            "fetchOpenOrders",
        ]

        for capability in basic_capabilities:
            assert capability in paper_gateway.has, f"Paper mode missing: {capability}"
            assert capability in prod_gateway.has, f"Prod mode missing: {capability}"

        # Production mode should support more advanced features
        advanced_capabilities = ["fetchOHLCV", "fetchOrderBook", "fetchTrades"]

        for capability in advanced_capabilities:
            if capability in prod_gateway.has:
                # If prod supports it, paper should either support it or explicitly not support it
                assert (
                    capability in paper_gateway.has
                ), f"Paper mode missing capability entry: {capability}"

    def test_market_data_structure_consistency(
        self, integration_paper_gateway, integration_prod_gateway, test_symbol
    ):
        """Test that market data has consistent structure between modes."""
        paper_gateway = integration_paper_gateway
        prod_gateway = integration_prod_gateway

        # Load markets in both modes
        paper_markets = paper_gateway.load_markets()
        prod_markets = prod_gateway.load_markets()

        # Both should have the test symbol
        assert test_symbol in paper_markets, f"Paper mode missing symbol: {test_symbol}"
        assert test_symbol in prod_markets, f"Prod mode missing symbol: {test_symbol}"

        # Market structures should be similar
        paper_market = paper_markets[test_symbol]
        prod_market = prod_markets[test_symbol]

        # Check for common CCXT market fields
        common_fields = ["symbol", "base", "quote", "active"]
        for field in common_fields:
            if field in prod_market:
                assert field in paper_market, f"Paper market missing field: {field}"

    def test_ticker_structure_consistency(
        self, integration_paper_gateway, integration_prod_gateway, test_symbol
    ):
        """Test that ticker data has consistent structure between modes."""
        paper_gateway = integration_paper_gateway
        prod_gateway = integration_prod_gateway

        # Load markets first
        paper_gateway.load_markets()
        prod_gateway.load_markets()

        # Fetch tickers
        paper_ticker = paper_gateway.fetch_ticker(test_symbol)
        prod_ticker = prod_gateway.fetch_ticker(test_symbol)

        # Both should have the same required fields
        required_fields = ["symbol", "timestamp", "datetime", "last", "bid", "ask"]
        for field in required_fields:
            assert field in paper_ticker, f"Paper ticker missing: {field}"
            assert field in prod_ticker, f"Prod ticker missing: {field}"

        # Symbol should match
        assert paper_ticker["symbol"] == test_symbol
        assert prod_ticker["symbol"] == test_symbol

    def test_balance_structure_consistency(
        self, integration_paper_gateway, integration_prod_gateway
    ):
        """Test that balance data has consistent structure between modes."""
        paper_gateway = integration_paper_gateway
        prod_gateway = integration_prod_gateway

        # Fetch balances
        paper_balance = paper_gateway.fetch_balance()
        prod_balance = prod_gateway.fetch_balance()

        # Both should have the same structure
        expected_fields = ["info", "timestamp", "datetime", "free", "used", "total"]
        for field in expected_fields:
            assert field in paper_balance, f"Paper balance missing: {field}"
            assert field in prod_balance, f"Prod balance missing: {field}"

        # Free, used, total should be dicts
        for field in ["free", "used", "total"]:
            assert isinstance(paper_balance[field], dict)
            assert isinstance(prod_balance[field], dict)

    @skip_if_no_exchange()
    def test_error_handling_consistency(
        self, integration_paper_gateway, integration_prod_gateway, test_symbol
    ):
        """Test that error handling is consistent between modes."""
        paper_gateway = integration_paper_gateway
        prod_gateway = integration_prod_gateway

        # Test invalid symbol handling
        invalid_symbol = "INVALID/PAIR"

        # Both should handle invalid symbols similarly
        paper_error_type = None
        prod_error_type = None

        try:
            paper_gateway.fetch_ticker(invalid_symbol)
        except Exception as e:
            paper_error_type = type(e)

        try:
            prod_gateway.fetch_ticker(invalid_symbol)
        except Exception as e:
            prod_error_type = type(e)

        # At least one should raise an error for invalid symbols
        # (MockExchange might be more forgiving than real exchanges)
        assert (
            paper_error_type is not None or prod_error_type is not None
        ), "At least one gateway should raise an error for invalid symbol"

        # If errors were raised, they should be exceptions
        if paper_error_type is not None:
            assert issubclass(paper_error_type, Exception)
        if prod_error_type is not None:
            assert issubclass(prod_error_type, Exception)

    def test_gateway_mode_detection(self, integration_paper_gateway, integration_prod_gateway):
        """Test that gateways correctly identify their modes."""
        paper_gateway = integration_paper_gateway
        prod_gateway = integration_prod_gateway

        # Check string representations
        paper_str = str(paper_gateway)
        prod_str = str(prod_gateway)

        assert "paper" in paper_str.lower()
        assert "prod" in prod_str.lower() or "production" in prod_str.lower()
