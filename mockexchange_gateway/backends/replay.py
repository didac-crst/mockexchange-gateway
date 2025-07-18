"""replay.py

Deterministic *replay backend* implementing the minimal HTTP interface
(`get`, `post`) expected by `MockExchangeGateway`, sourcing data from
pre-recorded events instead of a live server.

Motivation
----------
Allows:
    * Reproducible strategy tests using a fixed timeline of tickers.
    * Debugging by feeding historical sequences into higher-level code.
    * Offline development without network calls.

Scope (Initial Version)
-----------------------
* Supports ONLY read endpoints: `/tickers`, `/tickers/{symbol}`, `/balance`,
  `/orders`, `/orders/{oid}` and dry-run behavior for `can_execute`.
* Order creation (`POST /orders`) *simulates immediate fills* using
  current replay timestamp's symbol price (no partials / queue).
* Does **not** implement latency, partial fills, order book depth,
  or trade history. Extend if/when needed.

Data Format
-----------
Expected input is a dict (or JSON file you load) shaped like:

{
  "tickers": [
    {"timestamp": 1710000000000, "symbol": "BTC/USDT", "last": 50000, "bid": 49990, "ask": 50010},
    {"timestamp": 1710000000500, "symbol": "BTC/USDT", "last": 50010, "bid": 50000, "ask": 50020},
    ...
  ],
  "initial_balances": {
     "USDT": {"free": 10000.0, "used": 0.0},
     "BTC": {"free": 0.5, "used": 0.0}
  }
}

Tickers must be **sorted by timestamp** (client will not sort again).

Advancing Time
--------------
Call `advance(to_timestamp=None, steps=1)` to move the replay cursor forward.
The "current" ticker snapshot per symbol is updated as cursor advances.

YAGNI Principle
---------------
We intentionally omit candles, trades, websockets, and concurrency.
Add them only when the ecosystem needs them.
"""

from __future__ import annotations
from typing import Any, Mapping, Iterable, Dict, List, Optional
import bisect
import time

from ..exceptions import InsufficientFunds


class ReplayBackend:
    """Replay backend providing deterministic ticker & order behavior.

    Parameters
    ----------
    events:
        Dict with 'tickers' list and optional 'initial_balances'. See module docs.
    auto_advance:
        If True, each GET to `/tickers` advances one step automatically.
        Useful for simple iterative loops; set False for manual control.
    strict:
        If True, unknown symbols / missing tickers raise `KeyError`. If False,
        they return minimal placeholders (avoids hard failures during prototyping).

    Internal State
    --------------
    _tickers_by_symbol : dict[str, list[dict]]
        Pre-grouped tick events per symbol (sorted by timestamp).
    _cursor_index : dict[str, int]
        Current index into each symbol's ticker list (per-symbol timeline).
    _balances : dict[str, dict]
        Mutable balance store (similar to InMemoryBackend).
    _orders : dict[str, dict]
        Created orders keyed by oid.
    _oid_counter : int
        Monotonic sequence for order ids.
    """

    def __init__(self, events: Dict[str, Any], auto_advance: bool = False, strict: bool = True):
        tickers: List[Dict[str, Any]] = events.get("tickers", [])
        # Group tickers by symbol for O(1) per-symbol stepping.
        self._tickers_by_symbol: Dict[str, List[Dict[str, Any]]] = {}
        for t in tickers:
            self._tickers_by_symbol.setdefault(t["symbol"], []).append(t)

        # Ensure each symbol's list is sorted; cost is negligible at load.
        for symbol, lst in self._tickers_by_symbol.items():
            lst.sort(key=lambda r: r["timestamp"])

        self._cursor_index: Dict[str, int] = {s: 0 for s in self._tickers_by_symbol}

        # Balances
        init_bal = events.get("initial_balances", {"USDT": {"free": 10_000.0, "used": 0.0}})
        self._balances: Dict[str, Dict[str, float]] = {
            asset: {"free": v.get("free", 0.0), "used": v.get("used", 0.0)}
            for asset, v in init_bal.items()
        }

        self.auto_advance = auto_advance
        self.strict = strict

        self._orders: Dict[str, dict] = {}
        self._oid_counter: int = 0

    # ------------------------------------------------------------------
    # Time control
    # ------------------------------------------------------------------
    def advance(self, to_timestamp: Optional[int] = None, steps: int = 1):
        """Advance replay cursor.

        Parameters
        ----------
        to_timestamp:
            If provided, advance each symbol's cursor to the greatest index
            whose timestamp <= to_timestamp. Overrides `steps`.
        steps:
            Number of sequential ticks to move forward (per symbol) if
            `to_timestamp` is not given.

        Returns
        -------
        int
            New *maximum* timestamp across current per-symbol cursors.

        Rationale
        ---------
        Separating explicit time control from data requests gives test
        harnesses deterministic control. Auto-advance mode is only for
        quick scripts.
        """
        if to_timestamp is not None:
            for sym, lst in self._tickers_by_symbol.items():
                # Binary search to find rightmost index <= to_timestamp.
                ts_list = [x["timestamp"] for x in lst]
                idx = bisect.bisect_right(ts_list, to_timestamp) - 1
                if idx >= 0:
                    self._cursor_index[sym] = idx
            return self.current_timestamp()

        # Step each symbol forward bounded by list length.
        for sym, lst in self._tickers_by_symbol.items():
            new_idx = min(self._cursor_index[sym] + steps, len(lst) - 1)
            self._cursor_index[sym] = new_idx
        return self.current_timestamp()

    def current_timestamp(self) -> int:
        """Return the maximum current ticker timestamp across symbols.

        We use the *max* to represent "replay time" since different symbols
        could have asynchronous tick frequency.
        """
        ts = 0
        for sym, idx in self._cursor_index.items():
            lst = self._tickers_by_symbol[sym]
            if lst:
                ts = max(ts, lst[idx]["timestamp"])
        return ts

    # ------------------------------------------------------------------
    # HTTP-like interface
    # ------------------------------------------------------------------
    def get(self, path: str, params: Mapping[str, Any] | None = None):
        """Handle GET requests.

        Supported:
            /tickers
            /tickers/{symbol}
            /balance
            /orders
            /orders/{oid}

        Auto-advance:
            If `auto_advance` is True and path == '/tickers', we advance
            one step before returning (simulates streaming progression).
        """
        if path == "/tickers":
            if self.auto_advance:
                self.advance(steps=1)
            # Flatten current snapshot for all symbols.
            out = []
            for sym, idx in self._cursor_index.items():
                snap = self._tickers_by_symbol[sym][idx]
                out.append({**snap})
            return out

        if path.startswith("/tickers/"):
            symbol = path.split("/", 2)[2]
            if symbol not in self._tickers_by_symbol:
                if self.strict:
                    raise KeyError(f"Unknown symbol {symbol}")
                return {
                    "symbol": symbol,
                    "timestamp": self.current_timestamp(),
                    "last": None,
                    "bid": None,
                    "ask": None,
                }
            idx = self._cursor_index[symbol]
            snap = self._tickers_by_symbol[symbol][idx]
            return {**snap}

        if path == "/balance":
            assets = []
            for asset, b in self._balances.items():
                total = b["free"] + b["used"]
                assets.append(
                    {"asset": asset, "free": b["free"], "used": b["used"], "total": total}
                )
            return {"timestamp": self.current_timestamp(), "assets": assets}

        if path == "/orders":
            return list(self._orders.values())

        if path.startswith("/orders/"):
            oid = path.split("/", 2)[2]
            return self._orders[oid]

        raise KeyError(path)

    def post(self, path: str, json: Mapping[str, Any] | None = None, params=None):
        """Handle POST requests.

        Supported:
            /orders             -> create immediate-fill order
            /orders/{oid}/cancel
            /orders/can_execute

        Order Fill Logic
        ----------------
        Uses *current* snapshot price (last or midpoint if bid/ask present).
        No partial fills or slippage modeled—keeps deterministic behavior.

        Balance Adjustments
        -------------------
        Buy: deduct quote (USDT), add base.
        Sell: deduct base, add quote.

        Raises
        ------
        InsufficientFunds
            If balances insufficient for requested side/amount.
        KeyError
            On invalid paths.
        """
        if path == "/orders":
            self._oid_counter += 1
            oid = str(self._oid_counter)
            symbol = json["symbol"]
            side = json["side"]
            amt = float(json["amount"])
            price = self._resolve_price(symbol, json.get("price"))

            cost = amt * price
            if side == "buy":
                if self._balances.get("USDT", {}).get("free", 0.0) < cost:
                    raise InsufficientFunds("not enough USDT")
                self._balances["USDT"]["free"] -= cost
                base = symbol.split("/")[0]
                self._balances.setdefault(base, {"free": 0.0, "used": 0.0})
                self._balances[base]["free"] += amt
            else:  # sell
                base = symbol.split("/")[0]
                if self._balances.get(base, {"free": 0.0})["free"] < amt:
                    raise InsufficientFunds("not enough asset")
                self._balances[base]["free"] -= amt
                self._balances.setdefault("USDT", {"free": 0.0, "used": 0.0})
                self._balances["USDT"]["free"] += cost

            now = self.current_timestamp() or int(time.time() * 1000)
            order = {
                "oid": oid,
                "symbol": symbol,
                "side": side,
                "type": json["type"],
                "status": "filled",
                "price": price,
                "amount": amt,
                "filled": amt,
                "remaining": 0.0,
                "cost": cost,
                "created_at": now,
                "updated_at": now,
            }
            self._orders[oid] = order
            return order

        if path.endswith("/cancel"):
            oid = path.split("/")[-2]
            order = self._orders[oid]
            order["status"] = "canceled"
            order["updated_at"] = self.current_timestamp()
            return order

        if path == "/orders/can_execute":
            symbol = json["symbol"]
            side = json["side"]
            amt = float(json["amount"])
            price = self._resolve_price(symbol, json.get("price"))
            if side == "buy":
                can = self._balances.get("USDT", {}).get("free", 0.0) >= amt * price
            else:
                base = symbol.split("/")[0]
                can = self._balances.get(base, {"free": 0.0})["free"] >= amt
            return {"can_execute": can}

        raise KeyError(path)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_price(self, symbol: str, explicit_price: Any) -> float:
        """Pick a price for an order.

        Priority:
            1. Explicit user-provided price (limit order)
            2. Current tick 'last'
            3. Midpoint of bid/ask (if last missing)
            4. Fallback 0.0 (should rarely happen; indicates malformed data)

        Rationale
        ---------
        Centralizing price resolution avoids duplicating logic between
        create_order and can_execute paths.
        """
        if explicit_price is not None:
            return float(explicit_price)
        sym_ticks = self._tickers_by_symbol.get(symbol)
        if not sym_ticks:
            # Strict mode will already have errored earlier;
            # fallback for non-strict just returns 0.0 so tests can proceed.
            return 0.0
        snap = sym_ticks[self._cursor_index[symbol]]
        if snap.get("last") is not None:
            return float(snap["last"])
        bid = snap.get("bid")
        ask = snap.get("ask")
        if bid is not None and ask is not None:
            return (bid + ask) / 2.0
        return 0.0  # Final fallback (logged by callers if needed)
