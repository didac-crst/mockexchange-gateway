"""Integration tests for production mode (real exchanges).

These tests make real API calls to actual exchanges (in sandbox mode)
and verify that the gateway correctly handles the responses.
"""

import time

import pytest

from tests.helpers.credentials import skip_if_no_exchange


@pytest.mark.integration
@pytest.mark.prod
@skip_if_no_exchange()
class TestProductionModeIntegration:
    """Integration tests for production mode functionality."""

    def test_load_markets(self, integration_prod_gateway):
        """Test loading markets from real exchange."""
        gateway = integration_prod_gateway

        markets = gateway.load_markets()

        # Basic assertions about market structure
        assert isinstance(markets, dict)
        assert len(markets) > 0

        # Check that we have some common trading pairs
        common_pairs = ["BTC/USDT", "ETH/USDT"]
        found_pairs = [pair for pair in common_pairs if pair in markets]
        assert len(found_pairs) > 0, f"No common pairs found. Available: {list(markets.keys())[:5]}"

    def test_fetch_ticker(self, integration_prod_gateway, test_symbol):
        """Test fetching ticker data from real exchange."""
        gateway = integration_prod_gateway

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

    def test_fetch_balance(self, integration_prod_gateway):
        """Test fetching account balance from real exchange."""
        gateway = integration_prod_gateway

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

    def test_gateway_capabilities(self, integration_prod_gateway):
        """Test that gateway reports correct capabilities for production mode."""
        gateway = integration_prod_gateway

        # Check that has dict is populated
        assert isinstance(gateway.has, dict)
        assert len(gateway.has) > 0

        # Production mode should support more features than paper mode
        expected_supported = [
            "fetchTicker",
            "fetchBalance",
            "loadMarkets",
            "createOrder",
            "cancelOrder",
            "fetchOpenOrders",
            "fetchOHLCV",  # Most real exchanges support this
            "fetchOrderBook",  # Most real exchanges support this
        ]

        for feature in expected_supported:
            assert feature in gateway.has, f"Missing capability: {feature}"

    def test_fetch_ohlcv(self, integration_prod_gateway, test_symbol):
        """Test fetching OHLCV data from real exchange."""
        gateway = integration_prod_gateway

        # Load markets first
        gateway.load_markets()

        # Fetch recent OHLCV data
        ohlcv = gateway.fetch_ohlcv(test_symbol, "1h", limit=5)

        # Verify structure
        assert isinstance(ohlcv, list)
        assert len(ohlcv) > 0

        # Each candle should have [timestamp, open, high, low, close, volume]
        for candle in ohlcv:
            assert len(candle) >= 6, f"Invalid OHLCV candle: {candle}"
            assert isinstance(candle[0], int), "Timestamp should be int"
            assert all(
                isinstance(candle[i], (int, float)) for i in range(1, 6)
            ), "OHLCV values should be numeric"

    def test_fetch_order_book(self, integration_prod_gateway, test_symbol):
        """Test fetching order book from real exchange."""
        gateway = integration_prod_gateway

        # Load markets first
        gateway.load_markets()

        order_book = gateway.fetch_order_book(test_symbol)

        # Verify CCXT-compatible order book structure
        required_fields = ["symbol", "timestamp", "datetime", "bids", "asks"]
        for field in required_fields:
            assert field in order_book, f"Missing order book field: {field}"

        # Bids and asks should be lists of [price, amount] pairs
        assert isinstance(order_book["bids"], list)
        assert isinstance(order_book["asks"], list)

        # Verify bid/ask structure
        for bid in order_book["bids"][:3]:  # Check first few bids
            assert len(bid) == 2, f"Invalid bid: {bid}"
            assert isinstance(bid[0], (int, float)), "Bid price should be numeric"
            assert isinstance(bid[1], (int, float)), "Bid amount should be numeric"

        for ask in order_book["asks"][:3]:  # Check first few asks
            assert len(ask) == 2, f"Invalid ask: {ask}"
            assert isinstance(ask[0], (int, float)), "Ask price should be numeric"
            assert isinstance(ask[1], (int, float)), "Ask amount should be numeric"

    def test_rate_limiting(self, integration_prod_gateway, test_symbol):
        """Test that rate limiting works correctly."""
        gateway = integration_prod_gateway

        # Load markets first
        gateway.load_markets()

        # Make multiple rapid requests to test rate limiting
        start_time = time.time()

        for i in range(3):
            ticker = gateway.fetch_ticker(test_symbol)
            assert ticker["symbol"] == test_symbol

        end_time = time.time()

        # Should take at least some time due to rate limiting
        # (even if minimal, it should not be instant)
        assert end_time - start_time >= 0.1, "Rate limiting should add some delay"
