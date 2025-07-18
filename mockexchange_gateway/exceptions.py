class MockExchangeError(Exception):
    """Base exception."""


class HTTPError(MockExchangeError):
    def __init__(self, status: int, message: str, payload=None):
        super().__init__(f"[{status}] {message}")
        self.status = status
        self.payload = payload or {}


class AuthError(HTTPError):
    """401/403."""


class NotFoundError(HTTPError):
    """404."""


class InsufficientFunds(MockExchangeError):
    """Raised on insufficient balance (mapped from /orders/can_execute)."""
