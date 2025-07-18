"""inmemory.py

In-memory *test* backend that mimics the minimal HTTP client interface.

Purpose
-------
Provide a drop-in replacement for `HttpClient` during unit tests or
offline experimentation **without spinning up the real REST API**.

It implements `get()` and `post()` with the same signatures expected by
`MockExchangeGateway`, satisfying the `SupportsHTTPClient` protocol.

Scope & Limitations
-------------------
* All order fills are immediate and fully filled (status = "filled").
* No partial fills, order book depth, fees, slippage, or latency modeling.
* No persistence beyond process memory.
* Symbol existence is only validated if a ticker was seeded via `set_ticker`.

These constraints keep the fake deterministic and extremely fast while
still exercising higher-level client logic.
"""

from __future__ import annotations
import time
from typing import Any, Mapping
from ..exceptions import InsufficientFunds


class InMemoryBackend:
    """Simple offline backend emulating a subset of the server.

    Internal State
    --------------
    _tickers : dict[str, dict]
        Symbol -> ticker dict with at least 'last', 'bid', 'ask', 'timestamp'.
    _balances : dict[str, dict]
        Asset -> {"free": float, "used": float}. 'USDT' pre-funded for buys.
    _orders : dict[str, dict]
        Order id -> order record shaped like the real API response.
    _oid_counter : int
        Monotonic order id generator (stringified when exposed).

    Design Choices
    --------------
    * Keep structure close to server payloads to reduce translation code.
    * Avoid pydantic here for speed; models are applied higher up if needed.
    """

    def __init__(self):
        # Pre-fund quote asset so tests can place buys without extra setup.
        self._tickers: dict[str, dict] = {}
        self._balances: dict[str, dict] = {"USDT": {"free": 10_000.0, "used": 0.0}}
        self._orders: dict[str, dict] = {}
        self._oid_counter: int = 0

    # ------------------------------------------------------------------
    # HTTP-like interface (duck-typed)
    # ------------------------------------------------------------------
    def get(self, path: str, params: Mapping[str, Any] | None = None):
        """Handle GET requests.

        Supported paths:
            /tickers
            /tickers/{symbol}
            /balance
            /orders
            /orders/{oid}

        Parameters
        ----------
        path:
            Endpoint path identical to the real client usage.
        params:
            Ignored for now except reserved for future filtering.

        Returns
        -------
        list | dict
            Shape mimics server responses.

        Raises
        ------
        KeyError
            If path is unrecognized (helps catch typos in tests).
        """
        if path == "/tickers":
            # Flatten ticker store into list to match real API shape.
            return [
                {"symbol": k, "timestamp": v["timestamp"], **v}
                for k, v in self._tickers.items()
            ]
        if path.startswith("/tickers/"):
            symbol = path.split("/", 2)[2]
            return self._tickers[symbol]
        if path == "/balance":
            assets = []
            for asset, b in self._balances.items():
                total = b["free"] + b["used"]
                assets.append(
                    {"asset": asset, "free": b["free"], "used": b["used"], "total": total}
                )
            return {"timestamp": int(time.time() * 1000), "assets": assets}
        if path == "/orders":
            # NOTE: Ignoring params for simplicity; extend if tests need filtering.
            return list(self._orders.values())
        if path.startswith("/orders/"):
            oid = path.split("/", 2)[2]
            return self._orders[oid]
        raise KeyError(path)

    def post(self, path: str, json: Mapping[str, Any] | None = None, params=None):
        """Handle POST requests.

        Supported paths:
            /orders                -> create order (immediate fill)
            /orders/{oid}/cancel   -> cancel existing order
            /orders/can_execute    -> dry-run affordability check

        Parameters
        ----------
        path:
            Endpoint path.
        json:
            Request payload (symbol, side, type, amount, price).
        params:
            Unused placeholder for interface parity.

        Returns
        -------
        dict
            Order object or {'can_execute': bool} result.

        Raises
        ------
        InsufficientFunds
            If creating a buy without enough quote balance, or sell without asset.
        KeyError
            For unknown paths (ensures early failure for incorrect usage).

        Implementation Notes
        --------------------
        * Immediate full fills keep tests deterministic (no polling).
        * Price defaults to current ticker 'last' if not specified.
        """
        if path == "/orders":
            self._oid_counter += 1
            oid = str(self._oid_counter)
            symbol = json["symbol"]
            amount = float(json["amount"])
            # Fallback to last known price if limit price omitted (like market order).
            price = float(json.get("price") or self._tickers[symbol]["last"])
            side = json["side"]
            cost = amount * price

            if side == "buy":
                if self._balances["USDT"]["free"] < cost:
                    raise InsufficientFunds("not enough USDT")
                # Deduct quote, credit base.
                self._balances["USDT"]["free"] -= cost
                self._balances.setdefault(symbol.split("/")[0], {"free": 0.0, "used": 0.0})
                self._balances[symbol.split("/")[0]]["free"] += amount
            else:  # sell
                base = symbol.split("/")[0]
                if self._balances.get(base, {"free": 0})["free"] < amount:
                    raise InsufficientFunds("not enough asset")
                self._balances[base]["free"] -= amount
                self._balances["USDT"]["free"] += cost

            now_ms = int(time.time() * 1000)
            order = {
                "oid": oid,
                "symbol": symbol,
                "side": side,
                "type": json["type"],
                "status": "filled",        # All orders fill instantly in this fake backend.
                "price": price,
                "amount": amount,
                "filled": amount,
                "remaining": 0.0,
                "cost": cost,
                "created_at": now_ms,
                "updated_at": now_ms,
            }
            self._orders[oid] = order
            return order

        if path.endswith("/cancel"):
            oid = path.split("/")[-2]
            order = self._orders[oid]
            # Only mutate if not already terminal; simplistic approach is fine for tests.
            order["status"] = "canceled"
            return order

        if path == "/orders/can_execute":
            symbol = json["symbol"]
            side = json["side"]
            amount = float(json["amount"])
            price = float(json.get("price") or self._tickers[symbol]["last"])

            if side == "buy":
                can = self._balances["USDT"]["free"] >= amount * price
            else:
                base = symbol.split("/")[0]
                can = self._balances.get(base, {"free": 0.0})["free"] >= amount
            return {"can_execute": can}

        raise KeyError(path)

    # ------------------------------------------------------------------
    # Test Convenience Helpers
    # ------------------------------------------------------------------
    def set_ticker(self, symbol: str, last: float, bid=None, ask=None):
        """Seed or update a ticker used by subsequent calls.

        Parameters
        ----------
        symbol:
            Trading pair symbol (e.g. "BTC/USDT").
        last:
            Last trade price to set; also used as default for bid/ask if omitted.
        bid / ask:
            Optional explicit best bid/ask. If None, they default to `last`.

        Behavior
        --------
        * Timestamp is updated on every call to approximate "freshness".
        * Creating a ticker implicitly "registers" the market for the backend.

        Returns
        -------
        None

        Rationale
        ---------
        Keeping this API narrow (single setter) avoids multiple pathways to
        mutate internal test state, which can otherwise cause brittle tests.
        """
        self._tickers[symbol] = {
            "symbol": symbol,
            "last": last,
            "bid": bid or last,
            "ask": ask or last,
            "timestamp": int(time.time() * 1000),
        }
