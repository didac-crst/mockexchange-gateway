from __future__ import annotations
from typing import Any, Mapping, Iterable

from .client import HttpClient
from .models import Ticker, Order, Balance, BalanceAsset
from .utils import normalize_symbol
from .exceptions import InsufficientFunds


class MockExchangeGateway:
    """Subset of a CCXT exchange instance interface."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: float = 10.0,
        http_client: HttpClient | None = None,
    ):
        self._http = http_client or HttpClient(base_url, api_key, timeout)
        self._markets_cache: set[str] = set()

    # --- markets ----------------------------------------------------------
    def load_markets(self) -> list[str]:
        data = self._http.get("/tickers")
        self._markets_cache = {d["symbol"] for d in data}
        return sorted(self._markets_cache)

    def fetch_markets(self) -> list[dict[str, Any]]:
        if not self._markets_cache:
            self.load_markets()
        markets = []
        for sym in self._markets_cache:
            base, quote = sym.split("/")
            markets.append(
                {
                    "symbol": sym,
                    "base": base,
                    "quote": quote,
                    "active": True,
                    "precision": {},
                    "limits": {},
                    "info": {},
                }
            )
        return markets

    # --- tickers ----------------------------------------------------------
    def fetch_ticker(self, symbol: str) -> dict:
        symbol = normalize_symbol(symbol)
        raw = self._http.get(f"/tickers/{symbol}")
        return Ticker(**raw).model_dump()

    def fetch_tickers(self, symbols: Iterable[str] | None = None) -> dict[str, dict]:
        data = self._http.get("/tickers")
        tickers = {row["symbol"]: Ticker(**row).model_dump() for row in data}
        if symbols:
            symbols_set = {normalize_symbol(s) for s in symbols}
            tickers = {k: v for k, v in tickers.items() if k in symbols_set}
        return tickers

    # --- balance ----------------------------------------------------------
    def fetch_balance(self) -> dict:
        raw = self._http.get("/balance")
        assets = raw.get("assets", [])
        result = {"info": raw, "timestamp": raw.get("timestamp")}
        for a in assets:
            asset = a["asset"]
            result[asset] = {
                "free": a.get("free", 0.0),
                "used": a.get("used", 0.0),
                "total": a.get("total", 0.0),
            }
        return result

    # --- orders -----------------------------------------------------------
    def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> dict:
        body: dict[str, Any] = {
            "symbol": normalize_symbol(symbol),
            "type": type,
            "side": side,
            "amount": amount,
        }
        if price is not None:
            body["price"] = price
        if params:
            body.update(params)
        raw = self._http.post("/orders", json=body)
        return Order(**raw).model_dump()

    def fetch_order(self, order_id: str, symbol: str | None = None) -> dict:
        raw = self._http.get(f"/orders/{order_id}")
        return Order(**raw).model_dump()

    def fetch_orders(
        self,
        symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        tail: int | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {}
        if symbol:
            params["symbol"] = normalize_symbol(symbol)
        if status:
            params["status"] = status
        if side:
            params["side"] = side
        if tail:
            params["tail"] = tail
        data = self._http.get("/orders", params=params)
        return [Order(**o).model_dump() for o in data]

    def fetch_open_orders(self, symbol: str | None = None) -> list[dict]:
        return self.fetch_orders(symbol=symbol, status="open")

    def cancel_order(self, order_id: str) -> dict:
        raw = self._http.post(f"/orders/{order_id}/cancel")
        return Order(**raw).model_dump()

    # --- dry-run / margin check ------------------------------------------
    def can_execute_order(
        self, symbol: str, type: str, side: str, amount: float, price: float | None = None
    ) -> dict:
        body: dict[str, Any] = {
            "symbol": normalize_symbol(symbol),
            "type": type,
            "side": side,
            "amount": amount,
        }
        if price is not None:
            body["price"] = price
        resp = self._http.post("/orders/can_execute", json=body)
        if not resp.get("can_execute", True):
            raise InsufficientFunds(resp.get("reason", "Insufficient balance"))
        return resp
