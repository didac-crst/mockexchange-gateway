"""Integration test credential management.

This module provides utilities for managing API credentials needed for
integration testing with real exchanges and MockExchange instances.
"""

import os
from typing import Any, Dict, Optional

import pytest


def get_integration_config() -> Optional[Dict[str, Any]]:
    """Get integration test configuration from environment variables.

    Checks for required environment variables and returns configuration
    for both MockExchange (paper mode) and real exchanges (prod mode).

    Returns:
        Dict with configuration for both modes, or None if credentials missing

    Environment Variables:
        MOCKX_BASE_URL: MockExchange API base URL
        MOCKX_API_KEY: MockExchange API key (optional, defaults to 'dev-key')
        EXCHANGE_ID: Exchange identifier (e.g., 'binance', 'coinbase', 'kraken')
        EXCHANGE_API_KEY: Exchange API key (required for prod mode tests)
        EXCHANGE_SECRET: Exchange API secret (required for prod mode tests)
    """
    # Check if we have minimum required credentials
    if not os.getenv("MOCKX_BASE_URL"):
        return None

    config = {
        "mockexchange": {
            "base_url": os.getenv("MOCKX_BASE_URL"),
            "api_key": os.getenv("MOCKX_API_KEY", "dev-key"),
            "timeout": float(os.getenv("MOCKX_TIMEOUT", "10.0")),
        }
    }

    # Add real exchange config if credentials are available
    exchange_id = os.getenv(
        "EXCHANGE_ID", "binance"
    )  # Default to binance for backward compatibility
    exchange_key = os.getenv("EXCHANGE_API_KEY")
    exchange_secret = os.getenv("EXCHANGE_SECRET")

    if exchange_key and exchange_secret:
        config["exchange"] = {
            "exchange_id": exchange_id,
            "api_key": exchange_key,
            "secret": exchange_secret,
            "sandbox": True,  # Always use sandbox for tests
            "enableRateLimit": True,
        }

    return config


def skip_if_no_credentials():
    """Pytest marker to skip test if integration credentials not available.

    Usage:
        @skip_if_no_credentials()
        def test_integration_feature():
            # Test code that requires real API credentials
            pass
    """
    return pytest.mark.skipif(
        get_integration_config() is None,
        reason="Integration credentials not configured. Set MOCKX_BASE_URL at minimum.",
    )


def skip_if_no_exchange():
    """Pytest marker to skip test if exchange credentials not available.

    Usage:
        @skip_if_no_exchange()
        def test_exchange_integration():
            # Test code that specifically needs real exchange API access
            pass
    """
    config = get_integration_config()
    return pytest.mark.skipif(
        config is None or "exchange" not in config,
        reason="Exchange credentials not configured. Set EXCHANGE_API_KEY and EXCHANGE_SECRET.",
    )


def get_test_symbol() -> str:
    """Get a reliable symbol for testing.

    Returns a symbol that should be available on both MockExchange
    and most real exchanges for consistent testing.
    """
    return "BTC/USDT"


def get_test_amount() -> float:
    """Get a small amount for testing orders.

    Returns a very small amount to minimize costs and avoid
    minimum order size issues on real exchanges.
    """
    return 0.001  # 0.001 BTC


def is_integration_test_enabled() -> bool:
    """Check if integration tests should be run.

    Returns True if either:
    1. --integration flag was passed to pytest
    2. INTEGRATION_TESTS environment variable is set
    """
    return (
        os.getenv("INTEGRATION_TESTS", "").lower() in ("1", "true", "yes")
        or get_integration_config() is not None
    )
