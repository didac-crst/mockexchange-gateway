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
from pydantic import BaseModel, Field, model_validator
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

    model_config = {"populate_by_name": True}
    symbol: str
    timestamp: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    bid_volume: Optional[float] = Field(None, alias="bidVolume")
    ask_volume: Optional[float] = Field(None, alias="askVolume")

    @model_validator(mode="before")
    def _coerce_timestamp(cls, values):
        ts = values.get("timestamp")
        if ts is not None:
            # Accept string
            if isinstance(ts, str):
                try:
                    ts = float(ts)
                except ValueError:
                    ts = None
            if isinstance(ts, (int, float)):
                # Convert seconds to ms if clearly seconds
                if ts < 10**12:
                    ts = int(ts * 1000)
                else:
                    ts = int(ts)
                values["timestamp"] = ts
        return values

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

    model_config = {"populate_by_name": True}
    id: str = Field(alias="oid")
    symbol: str
    side: str
    type: str
    status: str
    ts_post: int
    amount: float
    price: float | None = None
    filled: float | None = None
    notion: float | None = None  # Alias for `cost` in some APIs
    cost: float | None = None
    remaining: float | None = None  # Computed field, not in server payload
    created_at: int | None = None
    updated_at: int | None = None
    ts_exec: int | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Compute remaining amount if not provided
        self._register_created_at()
        self._register_updated_at()
        self._register_cost()
        self._calculate_remaining()
    
    def _register_created_at(self):
        """Register the creation timestamp."""
        self.created_at = self.ts_post
        del self.ts_post
    
    def _register_updated_at(self):
        """Register the last updated timestamp."""
        self.updated_at = self.ts_exec
        del self.ts_exec
    
    def _register_cost(self):
        """Register the cost if not provided."""
        self.cost = self.notion
        del self.notion
    

    def _calculate_remaining(self):
        """Calculate remaining amount based on filled and total amount."""
        if self.filled is not None and self.amount is not None:
            self.remaining = self.amount - self.filled
