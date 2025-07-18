"""typing.py

Protocol (structural type) definitions for the gateway.

Why protocols?
--------------
We want to accept *any* object that behaves like our HTTP client (duck typing)
without forcing import-time coupling to a concrete class. This enables:

    * Injection of an in-memory backend for tests (no real HTTP)
    * Future swap to an async / different transport layer
    * Clean separation of concerns (facade code depends only on *behavior*)

Using `typing.Protocol` (PEP 544) lets static type checkers (mypy, pyright)
validate that supplied objects implement the required call signatures
without inheritance or explicit registration.
"""

from __future__ import annotations
from typing import Protocol, Any, Mapping


class SupportsHTTPClient(Protocol):
    """Minimal interface required by the gateway for an HTTP client.

    Methods
    -------
    get(path, params=None) -> Any
        Should perform a GET request and return a parsed representation
        (typically JSON-decoded Python primitives).
    post(path, json=None, params=None) -> Any
        Should perform a POST request with an optional JSON body.

    Design Choices
    --------------
    * Return type is `Any` because upstream pydantic models handle validation.
    * We do not include lower-level concerns (headers, timeout) here—those are
      implementation details of the concrete client (requests, httpx, in-memory).
    * Keeping the protocol surface *tiny* reduces friction for writing mocks.

    Example
    -------
    class Fake:
        def get(self, path, params=None):
            return {"ok": True}
        def post(self, path, json=None, params=None):
            return {"ok": True}

    fake = Fake()
    # Type checkers will accept `fake` wherever `SupportsHTTPClient` is expected.
    """

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        ...  # Ellipsis = interface only; implementations provide body.

    def post(
        self,
        path: str,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        ...
