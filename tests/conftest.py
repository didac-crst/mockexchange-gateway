"""tests/conftest.py

Pytest configuration & reusable fixtures.

This module provides shared fixtures and configuration for both unit and
integration tests in the MockX Gateway test suite.
"""

import pytest

from mockexchange_gateway import create_paper_gateway, create_prod_gateway
from tests.helpers.credentials import get_integration_config


def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires API credentials)",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if config.getoption("--integration"):
        # Running with --integration flag, don't skip integration tests
        return

    # Not running integration tests, skip them
    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def paper_gateway():
    """Create a paper mode gateway for testing.

    This fixture creates a gateway connected to a test MockExchange instance.
    It's suitable for unit tests that don't require real API credentials.
    """
    return create_paper_gateway(base_url="http://localhost:8000", api_key="test-key", timeout=5.0)


@pytest.fixture
def integration_config():
    """Get integration test configuration from environment.

    This fixture provides API credentials and configuration for integration
    tests. It will be None if credentials are not available.
    """
    return get_integration_config()


@pytest.fixture
def integration_paper_gateway(integration_config):
    """Create a paper mode gateway with real MockExchange credentials.

    This fixture creates a gateway connected to a real MockExchange instance
    using credentials from environment variables.
    """
    if integration_config is None:
        pytest.skip("Integration credentials not available")

    config = integration_config["mockexchange"]
    return create_paper_gateway(**config)


@pytest.fixture
def integration_prod_gateway(integration_config):
    """Create a production mode gateway with real exchange credentials.

    This fixture creates a gateway connected to a real exchange (in sandbox mode)
    using credentials from environment variables.
    """
    if integration_config is None or "exchange" not in integration_config:
        pytest.skip("Production mode credentials not available")

    config = integration_config["exchange"]
    return create_prod_gateway(**config)


@pytest.fixture
def test_symbol():
    """Get a test symbol that should work with both paper and prod modes."""
    return "BTC/USDT"


@pytest.fixture
def test_amount():
    """Get a small test amount for order testing."""
    return 0.001
