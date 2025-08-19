"""Unit tests for the MockX Gateway factory functions.

These tests verify the factory functions work correctly without making real API calls.
"""

from unittest.mock import patch

import pytest

from mockexchange_gateway import (
    MockXFactory,
    MockXGateway,
    create_paper_gateway,
    create_prod_gateway,
)


class TestFactoryFunctions:
    """Test the factory functions."""

    def test_create_paper_gateway(self):
        """Test creating a paper mode gateway."""
        gateway = create_paper_gateway(
            base_url="http://localhost:8000", api_key="test-key", timeout=5.0
        )

        assert isinstance(gateway, MockXGateway)
        assert gateway._mode == "paper"
        assert gateway._adapter.base_url == "http://localhost:8000"
        assert gateway._adapter.api_key == "test-key"
        assert gateway._adapter.timeout == 5.0

    def test_create_prod_gateway(self):
        """Test creating a production mode gateway."""
        gateway = create_prod_gateway(
            exchange_id="binance",
            api_key="test-key",
            secret="test-secret",
            sandbox=True,
        )

        assert isinstance(gateway, MockXGateway)
        assert gateway._mode == "prod"
        assert gateway._adapter.exchange_id == "binance"
        assert gateway._adapter.config["apiKey"] == "test-key"
        assert gateway._adapter.config["secret"] == "test-secret"
        assert gateway._adapter.config["sandbox"] is True

    def test_create_prod_gateway_without_credentials(self):
        """Test creating a production gateway without credentials."""
        gateway = create_prod_gateway(exchange_id="binance", sandbox=True)

        assert isinstance(gateway, MockXGateway)
        assert gateway._mode == "prod"
        assert gateway._adapter.exchange_id == "binance"
        assert gateway._adapter.config["sandbox"] is True
        assert "apiKey" not in gateway._adapter.config

    def test_factory_class_methods(self):
        """Test the factory class methods."""
        # Test paper gateway creation
        gateway1 = MockXFactory.create_paper_gateway(
            base_url="http://localhost:8000", api_key="test-key"
        )
        assert isinstance(gateway1, MockXGateway)
        assert gateway1._mode == "paper"

        # Test production gateway creation
        gateway2 = MockXFactory.create_prod_gateway(
            exchange_id="coinbase", api_key="test-key", secret="test-secret"
        )
        assert isinstance(gateway2, MockXGateway)
        assert gateway2._mode == "prod"

    def test_factory_with_additional_kwargs(self):
        """Test factory functions with additional keyword arguments."""
        gateway = create_prod_gateway(
            exchange_id="binance",
            api_key="test-key",
            secret="test-secret",
            sandbox=True,
            enableRateLimit=True,
            timeout=30000,
        )

        assert gateway._adapter.config["enableRateLimit"] is True
        assert gateway._adapter.config["timeout"] == 30000

    @patch("mockexchange_gateway.runtime.factory.ProdAdapter")
    def test_factory_error_handling(self, mock_prod_adapter):
        """Test factory error handling."""
        # Mock the adapter to raise an exception
        mock_prod_adapter.side_effect = Exception("Exchange not found")

        with pytest.raises(Exception) as exc_info:
            create_prod_gateway(exchange_id="nonexistent", api_key="test-key", secret="test-secret")

        assert "Exchange not found" in str(exc_info.value)
