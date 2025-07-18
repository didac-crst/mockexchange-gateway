from __future__ import annotations
from typing import Protocol, Any, Mapping


class SupportsHTTPClient(Protocol):
    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any: ...
    def post(
        self,
        path: str,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any: ...
