"""client.py

Synchronous minimal HTTP client wrapper used by the higher-level CCXT‑like
gateway. Abstracts:
    * Base URL handling (trailing slash normalization)
    * API key header injection
    * Request timeout configuration
    * Basic error mapping -> typed exceptions
    * JSON decoding with graceful fallback to raw text

Why not use `httpx` now?
-----------------------
We intentionally start with `requests` for:
    * Ubiquity / zero extra cognitive load
    * Simplicity for contributors
    * Lower surface area (no async complexity yet)

If / when an async variant is needed, we can introduce `AsyncHttpClient`
in a parallel module without breaking this sync API.
"""

from __future__ import annotations
from json import JSONDecodeError
import logging
from typing import Any, Mapping, Optional
import requests

from .exceptions import HTTPError, AuthError, NotFoundError
from .config import Settings

logger = logging.getLogger(__name__)


class HttpClient:
    """Thin synchronous HTTP client.

    Responsibilities:
        * Compose full request URLs
        * Inject `x-api-key` header when provided
        * Apply a per-request timeout
        * Convert non-2xx responses into semantic exceptions
        * Return parsed JSON (or raw text if decoding fails)

    Non‑goals:
        * Retries / backoff (leave to caller or future wrapper)
        * Rate limiting (not required for mock environment yet)
        * Session persistence beyond headers / connection pooling (Requests
          already provides keep-alive by default)

    Parameters
    ----------
    base_url:
        Root API endpoint. If `None`, loaded from environment via `Settings`.
    api_key:
        Optional key sent as `x-api-key`. Omit for unauthenticated dev.
    timeout:
        Float seconds for the request timeout.
    session:
        Optional pre-configured `requests.Session` (DI for tests or custom
        adapters, e.g., mocking, caching).
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ):
        # Allow environment-driven config for convenience in scripts / CI.
        if base_url is None:
            base_url = Settings.from_env().base_url
        # Defensive: trim trailing slash to avoid '//' when joining paths.
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        # Reuse a session for connection pooling (performance + fewer TCP handshakes).
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": "mockexchange-gateway/0.1.0"})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        """Perform a GET request.

        Parameters
        ----------
        path:
            Endpoint path starting with '/' (e.g. '/tickers').
        params:
            Optional query string mapping.

        Returns
        -------
        Any
            Parsed JSON (dict / list) or raw text / None.

        Rationale
        ---------
        Expose a *minimal* surface consumed by the higher-level gateway.
        Domain-specific semantics (e.g. symbol normalization) live elsewhere.
        """
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """Perform a POST request.

        Parameters
        ----------
        path:
            Endpoint path (e.g. '/orders').
        json:
            JSON-serializable body (already validated by caller).
        params:
            Optional query string mapping.

        Returns
        -------
        Any
            Parsed JSON (dict / list) or raw text / None.

        Design Choice
        -------------
        We don't support arbitrary content types yet—only JSON—because the
        current API surface is JSON-only. Extending later is straightforward.
        """
        return self._request("POST", path, params=params, json=json)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
    ):
        """Core request dispatcher.

        Handles:
            * URL construction
            * Header assembly (API key if present)
            * Status code branching -> exceptions
            * JSON decoding fallback

        Returns
        -------
        Any
            Parsed JSON payload, raw text, or `None` (empty body).

        Raises
        ------
        HTTPError | AuthError | NotFoundError
            For non-successful responses (status >= 400).
        """
        url = f"{self.base_url}{path}"
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        resp = self._session.request(
            method, url, params=params, json=json, headers=headers, timeout=self.timeout
        )

        if resp.status_code >= 400:
            self._raise_http(resp)

        # Some endpoints may legitimately return empty body (204 or 200 with no content).
        if not resp.text:
            return None
        try:
            return resp.json()  # Prefer structured data
        except JSONDecodeError:
            # Fallback: return raw text (debuggability > hard failure).
            return resp.text

    def _raise_http(self, resp):
        """Map an HTTP response to a domain exception.

        We attempt to extract a meaningful message from JSON payload keys
        commonly used by FastAPI (`detail`) or generic APIs (`message`).
        On failure to parse JSON, we degrade gracefully to the raw text.

        Raises
        ------
        AuthError
            For 401 / 403 codes.
        NotFoundError
            For 404 code.
        HTTPError
            For all other 4xx / 5xx codes.
        """
        status = resp.status_code
        try:
            payload = resp.json()
            message = payload.get("detail") or payload.get("message") or resp.text
        except Exception:
            payload = {}
            message = resp.text

        if status in (401, 403):
            raise AuthError(status, message, payload)
        if status == 404:
            raise NotFoundError(status, message, payload)
        raise HTTPError(status, message, payload)
