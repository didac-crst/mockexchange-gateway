"""Unit tests for the capabilities system.

These tests verify that capabilities are correctly reported for different modes.
"""

import pytest

from mockexchange_gateway import NotSupported
from mockexchange_gateway.core.capabilities import (
    get_capabilities,
    get_has_dict,
    has_feature,
    require_support,
)


class TestCapabilities:
    """Test the capabilities system."""

    def test_get_capabilities_paper_mode(self):
        """Test getting capabilities for paper mode."""
        capabilities = get_capabilities("paper")

        assert capabilities.mode == "paper"
        assert capabilities.has("fetchTicker") is True
        assert capabilities.has("fetchBalance") is True
        assert capabilities.has("loadMarkets") is True
        assert capabilities.has("createOrder") is True
        assert capabilities.has("fetchOHLCV") is False
        assert capabilities.has("fetchOrderBook") is False

    def test_get_capabilities_prod_mode(self):
        """Test getting capabilities for production mode."""
        capabilities = get_capabilities("prod")

        assert capabilities.mode == "prod"
        assert capabilities.has("fetchTicker") is True
        assert capabilities.has("fetchBalance") is True
        assert capabilities.has("loadMarkets") is True
        assert capabilities.has("createOrder") is True
        assert capabilities.has("fetchOHLCV") is True
        assert capabilities.has("fetchOrderBook") is True

    def test_has_feature_function(self):
        """Test the has_feature function."""
        assert has_feature("fetchTicker", "paper") is True
        assert has_feature("fetchTicker", "prod") is True
        assert has_feature("fetchOHLCV", "paper") is False
        assert has_feature("fetchOHLCV", "prod") is True

    def test_get_has_dict_paper_mode(self):
        """Test getting the has dict for paper mode."""
        has_dict = get_has_dict("paper")

        assert isinstance(has_dict, dict)
        assert has_dict["fetchTicker"] is True
        assert has_dict["fetchBalance"] is True
        assert has_dict["loadMarkets"] is True
        assert has_dict["createOrder"] is True
        assert has_dict["fetchOHLCV"] is False
        assert has_dict["fetchOrderBook"] is False

    def test_get_has_dict_prod_mode(self):
        """Test getting the has dict for production mode."""
        has_dict = get_has_dict("prod")

        assert isinstance(has_dict, dict)
        assert has_dict["fetchTicker"] is True
        assert has_dict["fetchBalance"] is True
        assert has_dict["loadMarkets"] is True
        assert has_dict["createOrder"] is True
        assert has_dict["fetchOHLCV"] is True
        assert has_dict["fetchOrderBook"] is True

    def test_require_support_supported_method(self):
        """Test require_support with a supported method."""
        # Should not raise an exception
        require_support("fetch_ticker", "paper")
        require_support("fetch_ticker", "prod")

    def test_require_support_unsupported_method(self):
        """Test require_support with an unsupported method."""
        with pytest.raises(NotSupported) as exc_info:
            require_support("fetch_ohlcv", "paper")

        assert "fetch_ohlcv" in str(exc_info.value).lower()
        assert "paper" in str(exc_info.value).lower()

    def test_capabilities_caching(self):
        """Test that capabilities are cached."""
        capabilities1 = get_capabilities("paper")
        capabilities2 = get_capabilities("paper")

        # Should be the same instance
        assert capabilities1 is capabilities2

    def test_method_name_mapping(self):
        """Test that method names are correctly mapped to capabilities."""
        capabilities = get_capabilities("paper")

        # Test snake_case to camelCase mapping
        assert capabilities.is_supported("fetch_ticker") is True
        assert capabilities.is_supported("fetch_balance") is True
        assert capabilities.is_supported("load_markets") is True
        assert capabilities.is_supported("create_order") is True
        assert capabilities.is_supported("fetch_ohlcv") is False

    def test_unknown_method_handling(self):
        """Test handling of unknown methods."""
        capabilities = get_capabilities("paper")

        # Unknown methods should return False
        assert capabilities.is_supported("unknown_method") is False
        assert capabilities.has("unknown_method") is False
