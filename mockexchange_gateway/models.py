"""models.py

Pydantic data models for normalizing responses from `mockexchange_api`.

Goals
-----
* Provide **schema validation**: detect breaking changes in server payloads early.
* Offer a stable, explicit contract for internal code and external users.
* Handle field aliasing (e.g. `bidVolume` -> `bid_volume`) so downstream
  code uses consistent Pythonic snake_case.

Design Notes
------------
* Pydantic is chosen for speed + ergonomics; if dependency footprint must
  shrink later, these can be swapped with dataclasses + manual validation.
* Keep models **lean**—add fields only when used. Over-modeling stale server
  fields causes unnecessary churn.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List


# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------
class Ticker(BaseModel):
    """Normalized ticker snapshot.

    Attributes
    ----------
    symbol:
        Market symbol (e.g. "BTC/USDT"). Uppercase expected.
    timestamp:
        Millisecond epoch timestamp when the server recorded the ticker.
    bid / ask:
        Current best bid / ask; may be None if not supplied.
    last:
        Last traded price (or equivalent mid if last not available).
    bid_volume / ask_volume:
        Depth at best bid / ask. Aliased from camelCase keys to snake_case.

    Rationale
    ---------
    * Keep only core fields required by UI / strategies; avoid speculative
      fields (e.g., high/low, vwap) until the API actually exposes them.
    """

    symbol: str
    timestamp: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    bid_volume: Optional[float] = Field(None, alias="bidVolume")
    ask_volume: Optional[float] = Field(None, alias="askVolume")

    class Config:
        populate_by_name = True  # Allow exporting snake_case with .model_dump(by_alias=False)


# ---------------------------------------------------------------------------
# Balance Models
# ---------------------------------------------------------------------------
class BalanceAsset(BaseModel):
    """Per-asset balance row.

    Attributes
    ----------
    asset:
        Asset code (e.g. "BTC", "USDT").
    free:
        Immediately available amount (not locked in orders).
    used:
        Amount currently reserved / locked.
    total:
        Convenience field (free + used) as supplied by server.

    Validation Approach
    -------------------
    Server already computes `total`; we do not recompute to avoid double
    source-of-truth. If inconsistency checking is desired, add a validator.
    """

    asset: str
    free: float
    used: float
    total: float


class Balance(BaseModel):
    """Aggregate balance snapshot.

    Attributes
    ----------
    timestamp:
        Millisecond epoch for snapshot capture time.
    assets:
        List of `BalanceAsset` entries (one per non-zero asset ideally).

    Why list instead of dict?
    -------------------------
    Ordered / repeated assets are unlikely, but using a list:
        * matches typical REST payload arrays
        * keeps JSON small (no duplicated keys)
    Conversion to dict is trivial where needed.
    """

    timestamp: int
    assets: List[BalanceAsset]


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
class Order(BaseModel):
    """Unified order representation.

    Attributes
    ----------
    id:
        Internal order id (alias from server key `oid`).
    symbol:
        Trading pair.
    side:
        "buy" or "sell".
    type:
        Order variety: "market", "limit" (extend as API grows).
    status:
        Lifecycle state (e.g. "open", "filled", "canceled").
    price:
        Limit price (None for pure market fills).
    amount:
        Original requested base amount.
    filled:
        Amount already executed.
    remaining:
        Amount left to fill (`amount - filled`).
    cost:
        Total quote currency spent/received (may be None until filled).
    created_at:
        Millisecond epoch creation time.
    updated_at:
        Millisecond epoch last update time (None if unchanged).

    Aliasing
    --------
    Server uses `oid`; we map it to `id` to mirror CCXT-style conventions.
    """

    id: str = Field(alias="oid")
    symbol: str
    side: str
    type: str
    status: str
    price: float | None = None
    amount: float
    filled: float
    remaining: float
    cost: float | None = None
    created_at: int
    updated_at: int | None = None

    class Config:
        allow_population_by_field_name = True  # Allows constructing with id=... in tests if desired.
