"""Unit tests for the MockX Gateway facade.

These tests verify the facade's behavior without making real API calls.
"""

from unittest.mock import Mock

import pytest

from mockexchange_gateway import MockXGateway
from mockexchange_gateway.adapters.paper import PaperAdapter
from mockexchange_gateway.adapters.prod import ProdAdapter


class TestMockXGateway:
    """Test the MockX Gateway facade."""

    def test_gateway_initialization_paper_mode(self):
        """Test gateway initialization with paper adapter."""
        adapter = PaperAdapter("http://localhost:8000", "test-key")
        gateway = MockXGateway(adapter)

        assert gateway._mode == "paper"
        assert isinstance(gateway._adapter, PaperAdapter)
        assert isinstance(gateway.has, dict)
        assert len(gateway.has) > 0

    def test_gateway_initialization_prod_mode(self):
        """Test gateway initialization with production adapter."""
        adapter = ProdAdapter("binance", {"sandbox": True})
        gateway = MockXGateway(adapter)

        assert gateway._mode == "prod"
        assert isinstance(gateway._adapter, ProdAdapter)
        assert isinstance(gateway.has, dict)
        assert len(gateway.has) > 0

    def test_gateway_string_representation(self):
        """Test gateway string representation."""
        adapter = PaperAdapter("http://localhost:8000", "test-key")
        gateway = MockXGateway(adapter)

        gateway_str = str(gateway)
        assert "MockXGateway" in gateway_str
        assert "paper" in gateway_str

    def test_gateway_capabilities_paper_mode(self):
        """Test that paper mode reports correct capabilities."""
        adapter = PaperAdapter("http://localhost:8000", "test-key")
        gateway = MockXGateway(adapter)

        # Paper mode should support basic features
        assert gateway.has.get("fetchTicker", False) is True
        assert gateway.has.get("fetchBalance", False) is True
        assert gateway.has.get("loadMarkets", False) is True
        assert gateway.has.get("createOrder", False) is True

        # Paper mode should NOT support advanced features
        assert gateway.has.get("fetchOHLCV", True) is False
        assert gateway.has.get("fetchOrderBook", True) is False

    def test_gateway_capabilities_prod_mode(self):
        """Test that production mode reports correct capabilities."""
        adapter = ProdAdapter("binance", {"sandbox": True})
        gateway = MockXGateway(adapter)

        # Production mode should support more features
        assert gateway.has.get("fetchTicker", False) is True
        assert gateway.has.get("fetchBalance", False) is True
        assert gateway.has.get("loadMarkets", False) is True
        assert gateway.has.get("createOrder", False) is True
        assert gateway.has.get("fetchOHLCV", False) is True
        assert gateway.has.get("fetchOrderBook", False) is True

    def test_gateway_delegates_to_adapter(self):
        """Test that gateway delegates calls to the adapter."""
        mock_adapter = Mock()
        mock_adapter.load_markets.return_value = {"BTC/USDT": {"symbol": "BTC/USDT"}}

        gateway = MockXGateway(mock_adapter)
        result = gateway.load_markets()

        mock_adapter.load_markets.assert_called_once()
        assert result == {"BTC/USDT": {"symbol": "BTC/USDT"}}

    def test_gateway_requires_support_for_unsupported_methods(self):
        """Test that gateway raises NotSupported for unsupported methods."""
        adapter = PaperAdapter("http://localhost:8000", "test-key")
        gateway = MockXGateway(adapter)

        from mockexchange_gateway import NotSupported

        with pytest.raises(NotSupported):
            gateway.fetch_ohlcv("BTC/USDT", "1h")

        with pytest.raises(NotSupported):
            gateway.fetch_order_book("BTC/USDT")
