from __future__ import annotations
import time
from typing import Any, Mapping
from ..exceptions import InsufficientFunds


class InMemoryBackend:
    """Simple offline backend implementing minimal subset for tests."""

    def __init__(self):
        self._tickers = {}
        self._balances = {"USDT": {"free": 10_000.0, "used": 0.0}}
        self._orders = {}
        self._oid_counter = 0

    # mimic HTTP client interface
    def get(self, path: str, params: Mapping[str, Any] | None = None):
        if path == "/tickers":
            return [{"symbol": k, "timestamp": v["timestamp"], **v} for k, v in self._tickers.items()]
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
            # naive ignoring params filtering for brevity
            return list(self._orders.values())
        if path.startswith("/orders/"):
            oid = path.split("/", 2)[2]
            return self._orders[oid]
        raise KeyError(path)

    def post(self, path: str, json: Mapping[str, Any] | None = None, params=None):
        if path == "/orders":
            self._oid_counter += 1
            oid = str(self._oid_counter)
            symbol = json["symbol"]
            amount = float(json["amount"])
            price = float(json.get("price") or self._tickers[symbol]["last"])
            side = json["side"]
            cost = amount * price
            # very naive balance update
            if side == "buy":
                if self._balances["USDT"]["free"] < cost:
                    raise InsufficientFunds("not enough USDT")
                self._balances["USDT"]["free"] -= cost
                self._balances.setdefault(symbol.split("/")[0], {"free": 0.0, "used": 0.0})
                self._balances[symbol.split("/")[0]]["free"] += amount
            else:  # sell
                base = symbol.split("/")[0]
                if self._balances.get(base, {"free": 0})["free"] < amount:
                    raise InsufficientFunds("not enough asset")
                self._balances[base]["free"] -= amount
                self._balances["USDT"]["free"] += cost
            order = {
                "oid": oid,
                "symbol": symbol,
                "side": side,
                "type": json["type"],
                "status": "filled",
                "price": price,
                "amount": amount,
                "filled": amount,
                "remaining": 0.0,
                "cost": cost,
                "created_at": int(time.time() * 1000),
                "updated_at": int(time.time() * 1000),
            }
            self._orders[oid] = order
            return order
        if path.endswith("/cancel"):
            oid = path.split("/")[-2]
            order = self._orders[oid]
            order["status"] = "canceled"
            return order
        if path == "/orders/can_execute":
            # simplistic check
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

    # helpers to inject data
    def set_ticker(self, symbol: str, last: float, bid=None, ask=None):
        self._tickers[symbol] = {
            "symbol": symbol,
            "last": last,
            "bid": bid or last,
            "ask": ask or last,
            "timestamp": int(time.time() * 1000),
        }
