"""adapters/paper.py

Paper adapter for MockExchange backend.

This adapter translates CCXT-style calls to MockExchange HTTP API calls
and converts responses back to CCXT format.
"""

from typing import Any, Dict, List, Optional

import requests

from ..config.symbols import normalize_symbol
from ..core.capabilities import require_support
from ..core.errors import (
    AuthenticationError,
    BadRequest,
    ExchangeError,
    InsufficientFunds,
    NetworkError,
    OrderNotFound,
    RequestTimeout,
)
from .mapping import DataMapper, ResponseMapper


class PaperAdapter:
    """Adapter for MockExchange backend (paper mode).

    This adapter provides a bridge between the CCXT-compatible facade and
    the MockExchange HTTP API. It translates CCXT-style method calls into
    HTTP requests to MockExchange and converts responses back to CCXT format.

    The paper adapter is designed for safe testing and development:
    - No real money is involved
    - Orders are simulated in MockExchange
    - Market data comes from MockExchange's internal state
    - Balances are managed by MockExchange

    This adapter ensures that trading strategies can be tested thoroughly
    before being deployed to production with real exchanges.

    Key responsibilities:
    1. **HTTP Communication**: Manages requests to MockExchange API
    2. **Data Translation**: Converts between MockExchange and CCXT formats
    3. **Error Handling**: Maps MockExchange errors to CCXT-style exceptions
    4. **Authentication**: Handles API key authentication with MockExchange
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key, "Content-Type": "application/json"})
        self._markets_cache: Dict[str, Any] = {}

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request to MockExchange.

        This is the core method for communicating with the MockExchange API.
        It handles HTTP requests, authentication, error handling, and response
        parsing. All adapter methods ultimately use this method to interact
        with MockExchange.

        The method includes:
        - Automatic authentication via API key header
        - Request timeout handling
        - HTTP error status code mapping
        - JSON response parsing
        - Network error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., "/tickers", "/orders")
            **kwargs: Additional request parameters (json, params, etc.)

        Returns:
            Any: Parsed JSON response from MockExchange

        Raises:
            RequestTimeout: If request times out
            NetworkError: If network connection fails
            AuthenticationError: If API key is invalid
            BadRequest: If request is malformed
            ExchangeError: For other HTTP errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)

            # Handle HTTP errors
            if response.status_code >= 400:
                self._handle_http_error(response)

            return response.json()

        except requests.exceptions.Timeout:
            raise RequestTimeout(f"Request timeout: {url}")
        except requests.exceptions.ConnectionError:
            raise NetworkError(f"Connection error: {url}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")
        except ValueError as e:
            raise ExchangeError(f"Invalid JSON response: {str(e)}")

    def _handle_http_error(self, response: requests.Response) -> None:
        """Handle HTTP error responses."""
        status_code = response.status_code

        try:
            error_data = response.json()
            message = error_data.get("message", error_data.get("error", "Unknown error"))
        except ValueError:
            message = response.text or f"HTTP {status_code}"

        if status_code == 400:
            raise BadRequest(message)
        elif status_code == 401:
            raise AuthenticationError(message)
        elif status_code == 404:
            raise OrderNotFound(message)
        elif status_code == 422:  # MockExchange uses 422 for insufficient funds
            raise InsufficientFunds(message)
        else:
            raise ExchangeError(f"HTTP {status_code}: {message}")

    # Market data methods
    def load_markets(self, reload: bool = False) -> Dict[str, Any]:
        """Load markets from MockExchange."""
        if not reload and self._markets_cache:
            return self._markets_cache

        data = self._make_request("GET", "/tickers")

        # Convert to CCXT format
        markets = {}
        for symbol in data:
            base, quote = symbol.split("/")
            market_data = {
                "symbol": symbol,
                "base": base,
                "quote": quote,
                "active": True,
                "precision": {},
                "limits": {},
                "info": {},
            }
            markets[symbol] = DataMapper.mockexchange_market_to_ccxt(market_data)

        self._markets_cache = markets
        return markets

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker for a symbol."""
        symbol = normalize_symbol(symbol, "paper")
        data = self._make_request("GET", f"/tickers/{symbol}")

        # Handle MockExchange response format
        if isinstance(data, dict) and symbol in data:
            ticker_data = data[symbol]
        else:
            ticker_data = data

        return DataMapper.mockexchange_ticker_to_ccxt(ticker_data)

    def fetch_tickers(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch tickers for multiple symbols.

        Note: MockExchange's /tickers endpoint returns a list of symbols, not ticker data.
        To get actual ticker data, we need to fetch individual tickers or use the
        comma-separated symbols endpoint.
        """
        # Get the list of symbols to fetch
        if symbols:
            # Use provided symbols
            symbols_to_fetch = [normalize_symbol(s, "paper") for s in symbols]
        else:
            # Get all available symbols from MockExchange
            symbols_list = self._make_request("GET", "/tickers")
            if not symbols_list:
                return {}
            # Use all available symbols (no limit to match CCXT behavior)
            symbols_to_fetch = symbols_list

        # Fetch tickers for the symbols using comma-separated endpoint
        symbols_str = ",".join(symbols_to_fetch)

        try:
            data = self._make_request("GET", f"/tickers/{symbols_str}")
            result = {}
            for symbol, ticker_data in data.items():
                result[symbol] = DataMapper.mockexchange_ticker_to_ccxt(ticker_data)
            return result
        except Exception:
            # If bulk fetch fails, return empty dict
            return {}

    # Balance methods
    def fetch_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Fetch account balance.

        Args:
            asset: Optional specific asset to fetch balance for
        """
        if asset:
            # Fetch specific asset balance
            data = self._make_request("GET", f"/balance/{asset}")
            return DataMapper.mockexchange_balance_to_ccxt(data)
        else:
            # Fetch full balance
            data = self._make_request("GET", "/balance")
            return DataMapper.mockexchange_balance_to_ccxt(data)

    def fetch_balance_list(self) -> Dict[str, Any]:
        """Fetch list of assets with balances."""
        data = self._make_request("GET", "/balance/list")
        return data

    def deposit(
        self, asset: str, amount: float, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deposit asset to account.

        Note: This is MockExchange-specific and not part of standard CCXT.
        """
        deposit_data = {"amount": amount}
        if params:
            deposit_data.update(params)

        data = self._make_request("POST", f"/balance/{asset}/deposit", json=deposit_data)
        return data

    def withdraw(
        self, asset: str, amount: float, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Withdraw asset from account.

        Note: This is MockExchange-specific and not part of standard CCXT.
        """
        withdraw_data = {"amount": amount}
        if params:
            withdraw_data.update(params)

        data = self._make_request("POST", f"/balance/{asset}/withdrawal", json=withdraw_data)
        return data

    def can_execute_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Check if an order can be executed (dry run).

        Note: This is MockExchange-specific and not part of standard CCXT.
        """
        symbol = normalize_symbol(symbol, "paper")

        order_data = {
            "symbol": symbol,
            "type": type,
            "side": side,
            "amount": amount,
        }

        if price is not None:
            order_data["limit_price"] = price

        if params:
            order_data.update(params)

        data = self._make_request("POST", "/orders/can_execute", json=order_data)
        return data

    # Order methods
    def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create an order."""
        symbol = normalize_symbol(symbol, "paper")

        order_data = {
            "symbol": symbol,
            "type": type,
            "side": side,
            "amount": amount,
        }

        if price is not None:
            order_data["limit_price"] = price

        if params:
            order_data.update(params)

        data = self._make_request("POST", "/orders", json=order_data)
        return DataMapper.mockexchange_order_to_ccxt(data)

    def fetch_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Fetch a specific order."""
        data = self._make_request("GET", f"/orders/{order_id}")
        return DataMapper.mockexchange_order_to_ccxt(data)

    def fetch_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch orders."""
        query_params = {}

        if symbol:
            query_params["symbol"] = normalize_symbol(symbol, "paper")
        if since:
            query_params["since"] = str(since)
        if limit:
            query_params["tail"] = str(limit)  # MockExchange uses 'tail' instead of 'limit'
        if params:
            query_params.update(params)

        data = self._make_request("GET", "/orders", params=query_params)
        orders = ResponseMapper.ensure_list_response(data)

        return [DataMapper.mockexchange_order_to_ccxt(order) for order in orders]

    def fetch_open_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch open orders.

        In MockExchange, open orders are those with status: 'new', 'partially_filled'
        """
        # MockExchange doesn't have a single "open" status, so we need to fetch all orders
        # and filter for open ones
        query_params = {}

        if symbol:
            query_params["symbol"] = normalize_symbol(symbol, "paper")
        if since:
            query_params["since"] = str(since)
        if limit:
            query_params["tail"] = str(limit)  # MockExchange uses 'tail' instead of 'limit'
        if params:
            query_params.update(params)

        # Fetch all orders and filter for open ones
        try:
            data = self._make_request("GET", "/orders", params=query_params)
            orders = ResponseMapper.ensure_list_response(data)

            # Filter for open orders (not in final state)
            open_statuses = {"new", "partially_filled"}
            open_orders = []

            for order in orders:
                order_status = order.get("status", "").lower()
                if order_status in open_statuses:
                    open_orders.append(DataMapper.mockexchange_order_to_ccxt(order))

            return open_orders

        except Exception:
            # Fallback to simpler orders/list endpoint
            data = self._make_request("GET", "/orders/list", params=query_params)
            # This returns a simpler format, we need to fetch full order details
            if isinstance(data, dict) and "orders" in data:
                order_ids = data["orders"]
                orders = []
                for order_id in order_ids:
                    try:
                        order_data = self._make_request("GET", f"/orders/{order_id}")
                        # Check if this order is open
                        order_status = order_data.get("status", "").lower()
                        if order_status in {"new", "partially_filled"}:
                            orders.append(DataMapper.mockexchange_order_to_ccxt(order_data))
                    except (requests.RequestException, ValueError, KeyError):
                        # Skip orders that can't be fetched due to network or data issues
                        continue
                return orders
            return []

    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an order."""
        data = self._make_request("POST", f"/orders/{order_id}/cancel")

        # MockExchange returns the canceled order in a nested structure
        if isinstance(data, dict) and "canceled_order" in data:
            order_data = data["canceled_order"]
        else:
            order_data = data

        return DataMapper.mockexchange_order_to_ccxt(order_data)

    def fetch_my_trades(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch user's trade history."""
        # MockExchange doesn't have a trades endpoint yet
        # Return empty list for now
        return []

    # Unsupported methods (will raise NotSupported)
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch OHLCV data (not supported in paper mode)."""
        require_support("fetch_ohlcv", "paper")
        return []

    def fetch_order_book(self, symbol: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetch order book (not supported in paper mode)."""
        require_support("fetch_order_book", "paper")
        return {}

    def fetch_trades(
        self, symbol: str, since: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch public trades (not supported in paper mode)."""
        require_support("fetch_trades", "paper")
        return []

    def close(self) -> None:
        """Close the adapter and clean up resources."""
        if self.session:
            self.session.close()
