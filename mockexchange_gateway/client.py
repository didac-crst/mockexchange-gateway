from __future__ import annotations
import json
import logging
from typing import Any, Mapping, Optional
import requests

from .exceptions import HTTPError, AuthError, NotFoundError
from .config import Settings

logger = logging.getLogger(__name__)


class HttpClient:
    """Thin sync HTTP client."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ):
        if base_url is None:
            base_url = Settings.from_env().base_url
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": "mockexchange-gateway/0.1.0"})

    # --- public -----------------------------------------------------------
    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        return self._request("POST", path, params=params, json=json)

    # --- internal ---------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
    ):
        url = f"{self.base_url}{path}"
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        resp = self._session.request(
            method, url, params=params, json=json, headers=headers, timeout=self.timeout
        )

        if resp.status_code >= 400:
            self._raise_http(resp)

        if not resp.text:
            return None
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text

    def _raise_http(self, resp):
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
