from __future__ import annotations
import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "http://localhost:8000"
ENV_BASE_URL = "MOCKEXCHANGE_BASE_URL"
ENV_API_KEY = "MOCKEXCHANGE_API_KEY"


@dataclass(slots=True)
class Settings:
    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=os.getenv(ENV_BASE_URL, DEFAULT_BASE_URL).rstrip("/"),
            api_key=os.getenv(ENV_API_KEY),
            timeout=float(os.getenv("MOCKEXCHANGE_TIMEOUT", "10")),
        )
