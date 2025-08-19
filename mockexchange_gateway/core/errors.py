"""core/errors.py

CCXT-style error classes for the MockX Gateway.

This module provides error classes that match CCXT's error hierarchy,
ensuring compatibility with existing CCXT code.
"""

from typing import Any, Dict, Optional


class MockXError(Exception):
    """Base exception for all MockX Gateway errors.

    This is the root exception class for all errors in the MockX Gateway.
    It provides a common interface for error handling and includes additional
    context information that can be useful for debugging and error reporting.

    The MockXError class extends the standard Python Exception with additional
    fields for response data and status information, making it easier to
    understand what went wrong when errors occur.

    Attributes:
        message: Human-readable error message
        response: Raw response data from the backend (if available)
        status: HTTP status code or other status information (if available)
    """

    def __init__(self, message: str, response: Optional[str] = None, status: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.response = response
        self.status = status


class ExchangeError(MockXError):
    """Base exception for exchange-related errors."""

    pass


class AuthenticationError(ExchangeError):
    """Authentication failed."""

    pass


class PermissionDenied(AuthenticationError):
    """Permission denied."""

    pass


class AccountNotEnabled(AuthenticationError):
    """Account not enabled."""

    pass


class AccountSuspended(AuthenticationError):
    """Account suspended."""

    pass


class BadRequest(ExchangeError):
    """Bad request."""

    pass


class BadSymbol(BadRequest):
    """Bad symbol."""

    pass


class BadResponse(BadRequest):
    """Bad response."""

    pass


class NullResponse(BadResponse):
    """Null response."""

    pass


class InsufficientFunds(ExchangeError):
    """Insufficient funds."""

    pass


class InvalidOrder(ExchangeError):
    """Invalid order."""

    pass


class OrderNotFound(InvalidOrder):
    """Order not found."""

    pass


class OrderNotCached(InvalidOrder):
    """Order not cached."""

    pass


class CancelPending(InvalidOrder):
    """Cancel pending."""

    pass


class OrderImmediatelyFillable(InvalidOrder):
    """Order immediately fillable."""

    pass


class OrderNotFillable(InvalidOrder):
    """Order not fillable."""

    pass


class DuplicateOrderId(InvalidOrder):
    """Duplicate order ID."""

    pass


class NotSupported(ExchangeError):
    """Operation not supported.

    Raised when a user attempts to use a feature that is not available
    in the current mode or backend. This is a key part of the gateway's
    design - it provides clear feedback when features aren't supported
    rather than silently failing or providing incorrect behavior.

    This exception is commonly raised in paper mode when trying to use
    features that MockExchange doesn't yet support, such as OHLCV data
    or order book depth. It helps users understand the limitations of
    each mode and plan their strategies accordingly.

    The error message typically includes guidance on how to work around
    the limitation or switch to a different mode that supports the feature.
    """

    pass


class NetworkError(MockXError):
    """Network error."""

    pass


class DDoSProtection(NetworkError):
    """DDoS protection."""

    pass


class RateLimitExceeded(NetworkError):
    """Rate limit exceeded."""

    pass


class ExchangeNotAvailable(NetworkError):
    """Exchange not available."""

    pass


class InvalidNonce(NetworkError):
    """Invalid nonce."""

    pass


class RequestTimeout(NetworkError):
    """Request timeout."""

    pass


class ErrorMapper:
    """Map MockExchange errors to CCXT-style errors."""

    @staticmethod
    def map_mockexchange_error(
        error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> MockXError:
        """Map MockExchange errors to CCXT-style errors."""

        # If it's already a MockX error, return as is
        if isinstance(error, MockXError):
            return error

        error_message = str(error)

        # Map common MockExchange error patterns
        if "insufficient" in error_message.lower() or "balance" in error_message.lower():
            return InsufficientFunds(error_message)

        elif "not found" in error_message.lower() or "does not exist" in error_message.lower():
            return OrderNotFound(error_message)

        elif "invalid" in error_message.lower() or "bad" in error_message.lower():
            return BadRequest(error_message)

        elif "timeout" in error_message.lower():
            return RequestTimeout(error_message)

        elif "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
            return AuthenticationError(error_message)

        elif "not supported" in error_message.lower() or "not implemented" in error_message.lower():
            return NotSupported(error_message)

        elif "network" in error_message.lower() or "connection" in error_message.lower():
            return NetworkError(error_message)

        # Default to generic exchange error
        return ExchangeError(error_message)

    @staticmethod
    def map_http_status(status_code: int, message: str) -> MockXError:
        """Map HTTP status codes to CCXT-style errors."""

        if status_code == 400:
            return BadRequest(message)
        elif status_code == 401:
            return AuthenticationError(message)
        elif status_code == 403:
            return PermissionDenied(message)
        elif status_code == 404:
            return OrderNotFound(message)
        elif status_code == 429:
            return RateLimitExceeded(message)
        elif status_code == 500:
            return ExchangeError(message)
        elif status_code == 502:
            return ExchangeNotAvailable(message)
        elif status_code == 503:
            return ExchangeNotAvailable(message)
        elif status_code == 504:
            return RequestTimeout(message)
        else:
            return ExchangeError(f"HTTP {status_code}: {message}")


def raise_not_supported(method_name: str, mode: str) -> None:
    """Raise NotSupported error for unsupported methods.

    This is a convenience function that creates and raises a NotSupported
    exception with a standardized error message. It's used throughout the
    gateway to provide consistent error messages when features aren't
    available in the current mode.

    The error message includes:
    - The name of the method that's not supported
    - The current mode (paper/prod)
    - Guidance on how to work around the limitation

    This function helps maintain consistency in error messages and makes
    it easier for users to understand what went wrong and how to fix it.

    Args:
        method_name: The name of the method that's not supported
        mode: The current operation mode (paper/prod)

    Raises:
        NotSupported: Always raised with a descriptive error message
    """
    raise NotSupported(
        f"{method_name} not supported in MODE={mode} (MockExchange backend). "
        f"Switch MODE=prod or use your backtest data tool."
    )
