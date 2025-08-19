"""Core package for MockX Gateway."""

from .capabilities import (
    Capabilities,
    get_capabilities,
    get_has_dict,
    has_feature,
    require_support,
)
from .errors import (
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
from .facade import MockXGateway

__all__ = [
    "MockXGateway",
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
    "get_capabilities",
    "has_feature",
    "get_has_dict",
    "require_support",
    "Capabilities",
]
