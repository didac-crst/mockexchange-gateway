"""ccxt_like.py

High-level CCXT-style facade for the mockexchange_api.

This module exposes a minimal subset of methods that *approximate* a CCXT
exchange instance (e.g. `fetch_ticker`, `create_order`, `fetch_balance`).
The goal is **API shape familiarity** without re‑implementing CCXT internals.

Design principles:
    * Keep the client *thin* – no business logic duplication (matching,
      fee calculation, etc.) that rightly belongs on the back-end.
    * Normalize responses via pydantic models (Ticker, Order) to ensure
      stable return shapes and to catch schema drift early.
    * Provide *incremental* expansion: add new methods only when another
      repo actually depends on them.
    * Favor explicitness over magical dynamic attribute construction
      (unlike full CCXT) to keep maintenance cost low.

If you later introduce an async variant, mirror this file as `ccxt_like_async.py`
with identical public method names for easy substitution.
"""

from __future__ import annotations
from typing import Any, Mapping, Iterable
import time

from .client import HttpClient
from .models import Ticker, Order
from .utils import normalize_symbol
from .exceptions import InsufficientFunds


class MockExchangeGateway:
    """Thin CCXT‑like gateway to `mockexchange_api`.

    This class intentionally implements **only** the subset of CCXT-style
    methods needed by the mockexchange ecosystem right now. Each method
    maps 1‑to‑1 onto a REST endpoint and returns *validated* / *normalized*
    Python primitives (dicts) derived from pydantic models.

    Parameters
    ----------
    base_url:
        Root URL of the mockexchange API (default: `http://localhost:8000`).
    api_key:
        Optional API key sent as `x-api-key`. Pass `None` for unsecured dev.
    timeout:
        Request timeout (seconds) used by the underlying HTTP client.
    http_client:
        Injectable client (must satisfy the small interface of `HttpClient`).
        This enables dependency injection for tests (*e.g.* in‑memory backend).

    Notes
    -----
    * We cache markets (symbols) after the first `load_markets()` to avoid
      repetitive network round‑trips.
    * Return types are simple dicts (instead of keeping pydantic instances)
      to resemble the ergonomics of CCXT's native returns.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: float = 10.0,
        http_client: HttpClient | None = None,
    ):
        # Allow test injection (in-memory backend) without patching.
        self._http = http_client or HttpClient(base_url, api_key, timeout)
        # Cache of discovered symbols (populated by load_markets()).
        self._markets_cache: set[str] = set()

    # ---------------------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------------------

    def _unwrap_symbol_mapping(self, payload, symbol: str):
        """Extract a single symbol's data from a mapping response."""
        if isinstance(payload, dict) and symbol in payload:
            return payload[symbol]
        return payload
    
    @staticmethod
    def _current_timestamp() -> int:
        """Return the current timestamp in milliseconds."""
        # Use time.time() to get the current time in seconds, then convert to milliseconds.
        return int(time.time() * 1000)

    # ---------------------------------------------------------------------
    # Markets
    # ---------------------------------------------------------------------
    def load_markets(self) -> list[str]:
        """Load and cache available symbols.

        Returns
        -------
        list[str]
            Sorted list of symbol strings like `"BTC/USDT"`.

        Rationale
        ---------
        CCXT typically preloads market metadata; here we only store symbols
        because deeper metadata (precision, limits) is not yet supplied by
        the back-end. Expanding to richer metadata remains trivial later.
        """
        data = self._http.get("/tickers")
        self._markets_cache = {d:{"symbol":d} for d in data}
        return sorted(self._markets_cache)

    def fetch_markets(self) -> list[dict[str, Any]]:
        """Return minimal market metadata for all cached symbols.

        Returns
        -------
        list[dict]
            Each dict contains a CCXT-inspired structure:
            `symbol`, `base`, `quote`, `active`, `precision`, `limits`, `info`.

        Behavior
        --------
        Auto-calls `load_markets()` if the cache is empty to match the
        expectation that `fetch_markets()` is always self-sufficient.

        Why minimal?
        ------------
        Avoid inventing fake precision/limit data that the back-end does not
        guarantee. We expose empty dicts so downstream code *must not* rely
        on fabricated constraints.
        """
        if not self._markets_cache:
            self.load_markets()
        markets: list[dict[str, Any]] = []
        for sym in self._markets_cache:
            base, quote = sym.split("/")
            markets.append(
                {
                    "symbol": sym,
                    "base": base,
                    "quote": quote,
                    "active": True,     # Assume active until API supplies status.
                    "precision": {},    # Placeholder for future numeric precision info.
                    "limits": {},       # Placeholder for future min/max sizes.
                    "info": {},         # Raw exchange-specific metadata (none yet).
                }
            )
        return markets

    # ---------------------------------------------------------------------
    # Tickers
    # ---------------------------------------------------------------------
    def fetch_ticker(self, symbol: str) -> dict:
        """Fetch the latest ticker for a single symbol.

        Parameters
        ----------
        symbol:
            Market symbol (case-insensitive); normalized to uppercase.

        Returns
        -------
        dict
            Normalized ticker fields (as produced by `Ticker.model_dump()`):
            `symbol`, `timestamp`, `bid`, `ask`, `last`, `bid_volume`, `ask_volume`.

        Notes
        -----
        * Normalization ensures consistent casing & missing field defaults.
        * We return a plain dict (not the pydantic object) for ergonomic parity
          with typical CCXT usage patterns.
        """
        symbol = normalize_symbol(symbol)
        raw = self._http.get(f"/tickers/{symbol}")
        raw = self._unwrap_symbol_mapping(raw, symbol)
        if not raw:
            raise ValueError(f"No ticker data found for symbol '{symbol}'")
        if isinstance(raw, str):
            # If the API returns a string (e.g. "Not found"), we raise an error.
            raise ValueError(f"Unexpected response for ticker '{symbol}': {raw}")
        if not isinstance(raw, dict):
            # If the API returns a non-dict type, we raise an error.
            raise ValueError(f"Unexpected response type for ticker '{symbol}': {type(raw)}")
        if "symbol" not in raw:
            # If the symbol is not in the response, we raise an error.
            raise ValueError(f"Ticker response for '{symbol}' does not contain 'symbol' field.")
        if raw["symbol"] != symbol:
            # If the symbol in the response does not match the requested symbol, we raise an error.
            raise ValueError(f"Ticker response for '{symbol}' has mismatched 'symbol' field: {raw['symbol']}")
        # If we reach here, the response is valid and we can return the normalized ticker.
        # Note: We use model_dump() to ensure we return a dict with snake_case keys
        # even if the API returns camelCase or mixed-case keys.
        # This ensures consistent API surface for consumers.
        # print(f"Fetched ticker for {symbol}: {raw}")  # Uncomment for debugging
        # Uncomment the line above to see the raw response in debug logs.
        # print("Raw ticker data:", raw)  # Uncomment for debugging
        # Uncomment the line above to see the raw response in debug logs.
        # print("Normalized ticker data:", Ticker(**raw).model_dump())  # Uncomment for debugging
        # Uncomment the line above to see the normalized response in debug logs.
        # print("Returning normalized ticker data:", raw)  # Uncomment for debugging
        # Uncomment the line above to see the final response before returning.
        return Ticker(**raw).model_dump()

    def fetch_tickers(self, symbols: Iterable[str] | None = None) -> dict[str, dict]:
        """Fetch all tickers, optionally filtering to a subset.

        Parameters
        ----------
        symbols:
            Optional iterable of symbols. If provided, filtering is done **client-side**
            after a single `/tickers` request (reduces network chatter).

        Returns
        -------
        dict[str, dict]
            Mapping: symbol -> normalized ticker dict.

        Design Choice
        -------------
        We intentionally **do not** issue multiple network calls for each symbol
        to keep latency low; the back-end already returns the full cache.
        """
        # We need to know all the symbols available in the exchange to filter correctly.
        exchange_symbols = self._http.get("/tickers")
        if symbols:
            symbols_set = {normalize_symbol(s) for s in symbols}
            # Filter the exchange symbols to only those requested.
            # This is a client-side filter to avoid multiple network calls.
            symbols_list = [s for s in exchange_symbols if s in symbols_set]
        else:
            symbols_list = exchange_symbols
        if not symbols_list:
            raise ValueError("No symbols provided; cannot fetch tickers without symbols.")
        # Create a string of symbols to pass to the API.
        # This is a single network call to fetch all tickers at once.
        symbols_list_str = ",".join(symbols_list)
        tickers_list = self._http.get(f"/tickers/{symbols_list_str}")
        Tickers_dict = {s: Ticker(**t).model_dump() for s, t in tickers_list.items()}
        return Tickers_dict

    # ---------------------------------------------------------------------
    # Balance
    # ---------------------------------------------------------------------
    def fetch_balance(self) -> dict:
        """Return a CCXT-like balance structure.

        Returns
        -------
        dict
            Structure:
            {
              "info": <raw json>,
              "timestamp": <epoch ms>,
              "ASSET": {"free": float, "used": float, "total": float},
              ...
            }

        Why not strong models?
        ----------------------
        A dynamic set of asset codes makes a static pydantic schema awkward.
        We validate at the *asset row* level server-side; here we trust the
        schema and only construct the expected mapping.
        """
        raw = self._http.get("/balance")
        assets = raw.get("assets", [])
        result: dict[str, Any] = {"info": raw, "timestamp": raw.get("timestamp", self._current_timestamp())}
        for a in assets:
            asset = a["asset"]
            result[asset] = {
                "free": a.get("free", 0.0),
                "used": a.get("used", 0.0),
                "total": a.get("total", 0.0),
            }
        return result

    # ---------------------------------------------------------------------
    # Orders
    # ---------------------------------------------------------------------
    def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> dict:
        """Create a market or limit order.

        Parameters
        ----------
        symbol:
            Instrument symbol (e.g. `"BTC/USDT"`).
        type:
            `"market"` or `"limit"`.
        side:
            `"buy"` or `"sell"`.
        amount:
            Base asset amount.
        limit_price:
            Required for limit orders; ignored for pure market.
        params:
            Extra fields to forward verbatim (future extension point).

        Returns
        -------
        dict
            Normalized order representation.

        Validation Strategy
        -------------------
        We rely on the server's validation. On success we wrap the response
        in the `Order` model to catch field drift early.
        """
        body: dict[str, Any] = {
            "symbol": normalize_symbol(symbol),
            "type": type,
            "side": side,
            "amount": amount,
        }
        if price is not None:
            body["limit_price"] = price
        if params:
            body.update(params)
        raw = self._http.post("/orders", json=body)
        return Order(**raw).model_dump()

    def fetch_order(self, order_id: str, symbol: str | None = None) -> dict:
        """Fetch a single order by ID.

        Parameters
        ----------
        order_id:
            Server-assigned order identifier.
        symbol:
            Accepted for CCXT signature parity; currently unused.

        Returns
        -------
        dict
            Normalized order dict.

        Note
        ----
        The `symbol` parameter is retained for future server-side validation
        and to keep the signature drop-in compatible with CCXT wrappers.
        """
        raw = self._http.get(f"/orders/{order_id}")
        return Order(**raw).model_dump()

    def fetch_orders(
        self,
        symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        tail: int | None = None,
    ) -> list[dict]:
        """List orders with optional filters.

        Parameters
        ----------
        symbol:
            Restrict to a single trading pair.
        status:
            Filter by lifecycle state (e.g. `"open"`, `"filled"`, `"canceled"`).
        side:
            `"buy"` or `"sell"`.
        tail:
            If supported server-side: return only the *N* most recent orders.
        Returns
        -------
        list[dict]
            List of normalized order dicts.

        Implementation Detail
        ---------------------
        Only non-None filters are forwarded, keeping query strings tidy.
        """
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
        """Convenience shorthand for `fetch_orders(status='open')`.

        Parameters
        ----------
        symbol:
            Optional symbol filter.

        Returns
        -------
        list[dict]
            Open orders.
        """
        return self.fetch_orders(symbol=symbol, status="open")

    def cancel_order(self, order_id: str) -> dict:
        """Cancel a single order.

        Parameters
        ----------
        order_id:
            Identifier of the order to cancel.

        Returns
        -------
        dict
            Updated order object (post-cancellation).

        Note
        ----
        Even if the order is already terminal, server should return its
        current state; we simply propagate that.
        """
        raw = self._http.post(f"/orders/{order_id}/cancel")
        order_data = raw['canceled_order']
        return Order(**order_data).model_dump()

    # ---------------------------------------------------------------------
    # Dry-run / balance check
    # ---------------------------------------------------------------------
    def can_execute_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float | None = None,
    ) -> dict:
        """Dry-run: validate sufficient balance (margin) for a hypothetical order.

        Parameters
        ----------
        symbol:
            Instrument symbol.
        type:
            Order type (`market` or `limit`).
        side:
            `"buy"` or `"sell"`.
        amount:
            Base amount.
        price:
            Price for limit orders (optional for market).

        Returns
        -------
        dict
            Raw server response (e.g. `{ "can_execute": bool, "reason": ... }`).

        Raises
        ------
        InsufficientFunds
            If the server reports `can_execute == False`.

        Why raise?
        ----------
        Raising a semantic exception lets callers reuse their existing CCXT
        error handling paths (which often branch on exception *type* rather
        than inspecting a return dict).
        """
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
            # Preserve reason if supplied for user feedback.
            raise InsufficientFunds(resp.get("reason", "Insufficient balance"))
        return resp
