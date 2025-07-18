"""config.py

Centralized configuration helpers for the mockexchange-gateway client.

Goals
-----
* Provide a single source of truth for environment variable names.
* Offer a lightweight `Settings` dataclass used by default in the HTTP client.
* Keep *policy* (which env vars exist) separate from *mechanism* (HTTP logic),
  improving testability and preventing hidden global state.

Non-goals
---------
* Complex nested configuration trees.
* Validation beyond simple type casting (handled minimally here; more stringent
  validation can be added if config surface grows).
"""

from __future__ import annotations
import os
from dataclasses import dataclass

# --- Defaults & Environment Variable Keys ------------------------------------
# These constants are defined once to avoid "magic strings" scattered
# throughout the codebase. If a name changes, update here only.

DEFAULT_BASE_URL = "http://localhost:8000"          # Sensible local dev default.
ENV_BASE_URL = "MOCKEXCHANGE_BASE_URL"              # Override for different envs.
ENV_API_KEY = "MOCKEXCHANGE_API_KEY"                # Optional authentication key.
ENV_TIMEOUT = "MOCKEXCHANGE_TIMEOUT"                # Per-request timeout seconds.


@dataclass(slots=True)
class Settings:
    """Container for runtime settings.

    Attributes
    ----------
    base_url:
        Root URL of the mockexchange API (no trailing slash).
    api_key:
        Optional API key used for authenticated requests.
    timeout:
        HTTP timeout in seconds (float). Keep conservative to surface network issues early.

    Design Decisions
    ----------------
    * `dataclass` with `slots=True` for reduced per-instance memory & faster attribute access.
    * Keep fields explicit and minimal—only add when a second component needs a new parameter.
    """

    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        """Instantiate settings from environment variables.

        Precedence / Behavior:
            * Missing variables fall back to documented defaults.
            * Trailing slash on `base_url` is trimmed to avoid accidental '//' joins.
            * Timeout is parsed as float; invalid numeric strings will raise a ValueError
              early, rather than producing silent misconfiguration.

        Returns
        -------
        Settings
            A new Settings instance populated from `os.environ`.

        Why a classmethod?
        ------------------
        Enables dependency injection in tests:
            - You can call `Settings(base_url="http://test")` directly.
            - Or patch environment and call `Settings.from_env()`.
        """
        base_url = os.getenv(ENV_BASE_URL, DEFAULT_BASE_URL).rstrip("/")
        api_key = os.getenv(ENV_API_KEY)
        timeout_raw = os.getenv(ENV_TIMEOUT, "10")

        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            # Fail fast with a descriptive message to avoid silent fallback.
            raise ValueError(
                f"Invalid {ENV_TIMEOUT} value '{timeout_raw}' (must be float-coercible)."
            ) from exc

        return cls(base_url=base_url, api_key=api_key, timeout=timeout)
