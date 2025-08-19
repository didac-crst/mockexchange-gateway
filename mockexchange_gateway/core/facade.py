"""core/facade.py

CCXT-compatible facade for the MockX Gateway.

This module provides the main interface that mirrors CCXT's API,
delegating calls to the appropriate adapter based on the current mode.
"""

from typing import Any, Dict, List, Optional

from ..adapters.paper import PaperAdapter
from ..core.capabilities import get_has_dict, require_support


class MockXGateway:
    """CCXT-compatible gateway facade.

    This class provides a unified interface that works with both MockExchange
    (paper mode) and real exchanges via CCXT (production mode). It implements
    the CCXT API surface, ensuring that trading strategies can be written once
    and work seamlessly across different backends.

    The facade pattern here serves several purposes:
    1. **API Consistency**: Provides the same interface regardless of backend
    2. **Capability Management**: Handles feature availability through the has dict
    3. **Error Handling**: Translates backend-specific errors to CCXT-style errors
    4. **Data Normalization**: Ensures consistent data formats across backends

    This design allows users to write trading code that works with both
    MockExchange for testing and real exchanges for production, with zero
    code changes required when switching between modes.
    """

    def __init__(self, adapter):
        """Initialize the gateway with an adapter."""
        self._adapter = adapter

        # Determine mode based on adapter type

        if isinstance(adapter, PaperAdapter):
            mode = "paper"
        else:
            mode = "prod"

        self._mode = mode
        self._has = get_has_dict(mode)
        self._markets = {}

    @property
    def has(self) -> Dict[str, bool]:
        """Get capabilities dict (CCXT-style).

        Returns a dictionary indicating which features are supported by the
        current backend. This follows the CCXT convention and allows users
        to check feature availability before attempting to use them.

        The capabilities dict helps with graceful degradation - users can
        check if a feature is available and provide alternative implementations
        or fallback behavior when features are not supported.

        Returns:
            Dict[str, bool]: Dictionary mapping feature names to availability
        """
        return self._has

    @property
    def markets(self) -> Dict[str, Any]:
        """Get markets dict (CCXT-style)."""
        if not self._markets:
            self._markets = self.load_markets()
        return self._markets

    def market(self, symbol: str) -> Dict[str, Any]:
        """Get market info for a symbol (CCXT-style)."""
        if not self._markets:
            self._markets = self.load_markets()
        return self._markets.get(symbol, {})

    # Market data methods
    def load_markets(self, reload: bool = False) -> Dict[str, Any]:
        """Load and cache markets.

        Fetches market information from the backend and caches it locally.
        This is typically the first call made when initializing a trading
        strategy, as it provides information about available trading pairs
        and their specifications.

        The markets cache improves performance by avoiding repeated API calls
        for market data. The reload parameter allows forcing a refresh of
        the cache when needed.

        Args:
            reload: If True, force reload of markets even if cached

        Returns:
            Dict[str, Any]: Dictionary of market information keyed by symbol
        """
        self._markets = self._adapter.load_markets(reload)
        return self._markets

    def fetch_markets(self) -> Dict[str, Any]:
        """Fetch all markets."""
        return self.load_markets()

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker for a symbol."""
        return self._adapter.fetch_ticker(symbol)

    def fetch_tickers(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch tickers for multiple symbols."""
        return self._adapter.fetch_tickers(symbols)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch OHLCV data."""
        require_support("fetch_ohlcv", self._mode)
        return self._adapter.fetch_ohlcv(symbol, timeframe, since, limit)

    def fetch_order_book(self, symbol: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetch order book."""
        require_support("fetch_order_book", self._mode)
        return self._adapter.fetch_order_book(symbol, limit)

    def fetch_trades(
        self, symbol: str, since: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch public trades."""
        require_support("fetch_trades", self._mode)
        return self._adapter.fetch_trades(symbol, since, limit)

    # Balance methods
    def fetch_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Fetch account balance.

        Args:
            asset: Optional specific asset to fetch balance for
        """
        return self._adapter.fetch_balance(asset)

    def fetch_balance_list(self) -> Dict[str, Any]:
        """Fetch list of assets with balances."""
        if self._mode != "paper":
            raise NotSupported("fetch_balance_list is only available in paper mode (MockExchange).")
        return self._adapter.fetch_balance_list()
    # MockExchange-specific methods (not part of CCXT standard)
    def deposit(
        self, asset: str, amount: float, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deposit asset to account (MockExchange-specific)."""
        return self._adapter.deposit(asset, amount, params)

    def withdraw(
        self, asset: str, amount: float, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Withdraw asset from account (MockExchange-specific)."""
        return self._adapter.withdraw(asset, amount, params)

    def can_execute_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Check if an order can be executed (MockExchange-specific)."""
        return self._adapter.can_execute_order(symbol, type, side, amount, price, params)

    def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch open positions."""
        require_support("fetch_positions", self._mode)
        return self._adapter.fetch_positions(symbols)

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
        """Create an order.

        Places a new order on the exchange. This is the core trading operation
        that allows users to buy or sell assets. The method supports both
        market and limit orders with various parameters.

        In paper mode, this creates orders in MockExchange for safe testing.
        In production mode, this places real orders on the configured exchange.

        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            type: Order type ("market" or "limit")
            side: Order side ("buy" or "sell")
            amount: Quantity to trade
            price: Limit price (required for limit orders)
            params: Additional order parameters

        Returns:
            Dict[str, Any]: Order information including ID, status, and details

        Raises:
            InsufficientFunds: If account balance is insufficient
            InvalidOrder: If order parameters are invalid
            NotSupported: If order type is not supported
        """
        return self._adapter.create_order(symbol, type, side, amount, price, params)

    def fetch_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Fetch a specific order."""
        return self._adapter.fetch_order(order_id, symbol)

    def fetch_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch orders."""
        return self._adapter.fetch_orders(symbol, since, limit, params)

    def fetch_open_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch open orders."""
        return self._adapter.fetch_open_orders(symbol, since, limit, params)

    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an order."""
        return self._adapter.cancel_order(order_id, symbol)

    def fetch_my_trades(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch user's trade history."""
        return self._adapter.fetch_my_trades(symbol, since, limit, params)

    # Advanced features (production mode only)
    def fetch_leverage(self, symbol: str) -> Dict[str, Any]:
        """Fetch current leverage."""
        require_support("fetch_leverage", self._mode)
        return self._adapter.fetch_leverage(symbol)

    def set_leverage(self, leverage: int, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Set leverage."""
        require_support("set_leverage", self._mode)
        return self._adapter.set_leverage(leverage, symbol)

    def fetch_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Fetch funding rate."""
        require_support("fetch_funding_rate", self._mode)
        return self._adapter.fetch_funding_rate(symbol)

    def fetch_funding_history(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch funding history."""
        require_support("fetch_funding_history", self._mode)
        return self._adapter.fetch_funding_history(symbol)

    # Convenience methods
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a market order."""
        return self.create_order(symbol, "market", side, amount, params=params)

    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a limit order."""
        return self.create_order(symbol, "limit", side, amount, price, params)

    # Utility methods
    def close(self) -> None:
        """Close the gateway and clean up resources."""
        if self._adapter:
            self._adapter.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # String representation
    def __str__(self) -> str:
        return f"MockXGateway(mode={self._mode})"

    def __repr__(self) -> str:
        return self.__str__()
