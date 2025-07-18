"""utils.py

Small pure utility functions shared across the gateway.

Guidelines
----------
Keep this module **tiny** and side‑effect free:
    * Only stateless, deterministic helpers.
    * No network / IO / logging (harder to test & reason about).
    * If a function grows complex or domain‑specific, promote it to a
      dedicated module (avoids 'grab‑bag' anti‑pattern).

Rationale
---------
Centralizing these low-level helpers avoids duplicate ad‑hoc inline
implementations (e.g. inconsistent symbol handling) and gives a single
place to harden behavior later (normalization rules, validation, etc.).
"""

from __future__ import annotations
from typing import Iterable


def normalize_symbol(symbol: str) -> str:
    """Normalize a trading pair symbol (e.g. 'btc/usdt' -> 'BTC/USDT').

    Current normalization strategy is *uppercase only*. We deliberately
    **do not** reorder components or strip whitespace here to keep behavior
    predictable and minimal. Additional sanitation (like trimming spaces)
    can be added if real-world input indicates a need.

    Parameters
    ----------
    symbol:
        Raw symbol string provided by user / upstream code.

    Returns
    -------
    str
        Uppercased symbol.
    """
    return symbol.upper()


def split_symbol(symbol: str) -> tuple[str, str]:
    """Split a normalized symbol into (base, quote).

    Parameters
    ----------
    symbol:
        Expected format: 'BASE/QUOTE'. We *assume* correctness because
        upstream call sites control symbol generation (fail fast on ValueError).

    Returns
    -------
    (str, str)
        Tuple of base asset code and quote asset code.

    Why no graceful fallback?
    -------------------------
    A silent fallback (returning empty strings) would mask coding errors.
    Letting `symbol.split('/')` raise is a deliberate defensive choice.
    """
    base, quote = symbol.split("/")
    return base, quote


def ensure_set(iterable: Iterable[str]) -> set[str]:
    """Convert an iterable of strings to a set.

    Parameters
    ----------
    iterable:
        Any iterable producing strings (list, tuple, generator).

    Returns
    -------
    set[str]
        Materialized set of unique strings.

    Why this helper?
    ----------------
    Explicit helper documents intent ('we need uniqueness') and allows
    a future optimization (e.g., specialized symbol set class) without
    changing many call sites.
    """
    return set(iterable)
