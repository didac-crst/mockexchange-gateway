"""MockX Gateway

CCXT-compatible gateway for seamless switching between MockExchange (paper mode)
and real exchanges (production mode).

This package provides a unified interface that works with both MockExchange
for testing and real exchanges via CCXT for production trading.
"""

from .core.capabilities import get_has_dict, has_feature
from .core.errors import (
    AuthenticationError,
    BadRequest,
    BadSymbol,
    ExchangeError,
    InsufficientFunds,
    InvalidOrder,
    MockXError,
    NetworkError,
    NotSupported,
    OrderNotFound,
    RequestTimeout,
)
from .core.facade import MockXGateway
from .runtime.factory import MockXFactory, create_paper_gateway, create_prod_gateway

__version__ = "0.2.0"

__all__ = [
    # Main gateway class
    "MockXGateway",
    # Factory functions
    "create_paper_gateway",
    "create_prod_gateway",
    "MockXFactory",
    # Error classes
    "MockXError",
    "ExchangeError",
    "AuthenticationError",
    "BadRequest",
    "BadSymbol",
    "InsufficientFunds",
    "InvalidOrder",
    "OrderNotFound",
    "NotSupported",
    "NetworkError",
    "RequestTimeout",
    # Utility functions
    "get_has_dict",
    "has_feature",
]
