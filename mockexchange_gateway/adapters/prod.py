"""adapters/prod.py

Production adapter for CCXT backend.

This adapter provides a thin pass-through to CCXT exchange instances,
ensuring consistent interface with the paper adapter.
"""

from typing import Any, Dict, List, Optional

import ccxt

from ..config.symbols import normalize_symbol
from ..core.errors import ExchangeError


class ProdAdapter:
    """Adapter for CCXT backend (production mode).

    This adapter provides a thin wrapper around CCXT exchange instances for
    production trading. It maintains the same interface as the paper adapter
    while delegating actual operations to the underlying CCXT exchange.

    The production adapter is designed for live trading:
    - Connects to real exchanges via CCXT
    - Places actual orders with real money
    - Fetches live market data from exchanges
    - Manages real account balances and positions

    This adapter ensures that the same trading strategies that work in paper
    mode can be deployed to production with minimal changes, while providing
    access to the full feature set of CCXT and real exchanges.

    Key responsibilities:
    1. **CCXT Integration**: Manages CCXT exchange instances
    2. **Interface Consistency**: Maintains same API as paper adapter
    3. **Symbol Normalization**: Ensures consistent symbol formats
    4. **Error Propagation**: Passes through CCXT errors appropriately
    """

    def __init__(self, exchange_id: str, config: Dict[str, Any]):
        self.exchange_id = exchange_id
        self.config = config
        self._exchange = None
        self._markets_cache: Dict[str, Any] = {}
        self._initialize_exchange()

    def _initialize_exchange(self) -> None:
        """Initialize the CCXT exchange instance."""
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            self._exchange = exchange_class(self.config)

            # Load markets if not in sandbox mode
            if not self.config.get("sandbox", False) and self._exchange is not None:
                try:
                    self._exchange.load_markets()
                except Exception as e:
                    # Log warning but don't fail - markets can be loaded later
                    print(f"Warning: Could not load markets for {self.exchange_id}: {e}")

        except AttributeError:
            raise ExchangeError(f"Exchange '{self.exchange_id}' not found in CCXT")
        except Exception as e:
            raise ExchangeError(f"Failed to initialize {self.exchange_id}: {str(e)}")

    @property
    def exchange(self):
        """Get the underlying CCXT exchange instance."""
        if self._exchange is None:
            self._initialize_exchange()
        if self._exchange is None:  # Type guard
            raise RuntimeError("Failed to initialize exchange")
        return self._exchange

    # Market data methods
    def load_markets(self, reload: bool = False) -> Dict[str, Any]:
        """Load markets from CCXT."""
        if reload or not self._markets_cache:
            self._markets_cache = self.exchange.load_markets()

        return self._markets_cache

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker for a symbol."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_ticker(symbol)

    def fetch_tickers(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch tickers for multiple symbols."""
        if symbols:
            symbols = [normalize_symbol(s, "prod") for s in symbols]
            return self.exchange.fetch_tickers(symbols)
        else:
            return self.exchange.fetch_tickers()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch OHLCV data."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)

    def fetch_order_book(self, symbol: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetch order book."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_order_book(symbol, limit)

    def fetch_trades(
        self, symbol: str, since: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch public trades."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_trades(symbol, since, limit)

    # Balance methods
    def fetch_balance(self) -> Dict[str, Any]:
        """Fetch account balance."""
        return self.exchange.fetch_balance()

    def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch open positions."""
        return self.exchange.fetch_positions(symbols)

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
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.create_order(symbol, type, side, amount, price, params or {})

    def fetch_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Fetch a specific order."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_order(order_id, symbol)

    def fetch_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch orders."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_orders(symbol, since, limit, params or {})

    def fetch_open_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch open orders."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_open_orders(symbol, since, limit, params or {})

    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an order."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.cancel_order(order_id, symbol)

    def fetch_my_trades(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch user's trade history."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_my_trades(symbol, since, limit, params or {})

    # Advanced features
    def fetch_leverage(self, symbol: str) -> Dict[str, Any]:
        """Fetch current leverage."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_leverage(symbol)

    def set_leverage(self, leverage: int, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Set leverage."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.set_leverage(leverage, symbol)

    def fetch_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Fetch funding rate."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_funding_rate(symbol)

    def fetch_funding_history(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch funding history."""
        if symbol:
            symbol = normalize_symbol(symbol, "prod")
        return self.exchange.fetch_funding_history(symbol)

    # Properties that CCXT users expect
    @property
    def has(self) -> Dict[str, bool]:
        """Get the capabilities dict."""
        return self.exchange.has

    @property
    def markets(self) -> Dict[str, Any]:
        """Get the markets dict."""
        return self.exchange.markets

    def market(self, symbol: str) -> Dict[str, Any]:
        """Get market info for a symbol."""
        symbol = normalize_symbol(symbol, "prod")
        return self.exchange.market(symbol)

    def close(self) -> None:
        """Close the adapter and clean up resources."""
        if self._exchange:
            self._exchange.close()
