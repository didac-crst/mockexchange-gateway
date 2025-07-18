"""MockExchange Gateway

Thin CCXT-like client for the mockexchange_api back-end.
"""

from .ccxt_like import MockExchangeGateway
from .exceptions import (
    MockExchangeError,
    HTTPError,
    AuthError,
    NotFoundError,
    InsufficientFunds,
)

__all__ = [
    "MockExchangeGateway",
    "MockExchangeError",
    "HTTPError",
    "AuthError",
    "NotFoundError",
    "InsufficientFunds",
]

__version__ = "0.1.0"
