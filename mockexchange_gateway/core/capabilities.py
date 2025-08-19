"""core/capabilities.py

Capabilities system for the MockX Gateway.

This module defines what features are available in each mode (paper/prod)
and provides the `has` dict that CCXT users expect.
"""

from typing import Any, Dict


class Capabilities:
    """Capabilities manager for MockX Gateway.

    This class manages feature availability for different modes of the MockX Gateway.
    It provides a centralized way to determine which features are supported in
    paper mode (MockExchange) versus production mode (CCXT).

    The capabilities system serves several important purposes:
    1. **Feature Detection**: Allows users to check if features are available before using them
    2. **Graceful Degradation**: Enables fallback behavior when features aren't supported
    3. **Documentation**: Provides clear information about what works in each mode
    4. **Error Prevention**: Helps prevent runtime errors from unsupported features

    The capabilities are defined statically for each mode, reflecting the current
    state of MockExchange and CCXT feature support. As MockExchange adds new
    features, the paper mode capabilities can be updated accordingly.

    This design follows the CCXT convention of using a 'has' dictionary to
    indicate feature availability, ensuring compatibility with existing CCXT code.
    """

    # Paper mode capabilities (MockExchange)
    PAPER_CAPABILITIES = {
        # Core trading
        "createOrder": True,
        "cancelOrder": True,
        "fetchOrder": True,
        "fetchOrders": True,
        "fetchOpenOrders": True,
        "fetchClosedOrders": True,
        "fetchMyTrades": True,
        # Account
        "fetchBalance": True,
        "fetchBalanceList": True,  # MockExchange supports balance list
        "fetchPositions": False,  # MockExchange doesn't support futures
        # Market data
        "fetchTicker": True,
        "fetchTickers": True,
        "fetchOHLCV": False,  # Not implemented in MockExchange
        "fetchOrderBook": False,  # Not implemented in MockExchange
        "fetchTrades": False,  # Not implemented in MockExchange
        # Metadata
        "loadMarkets": True,
        "fetchMarkets": True,
        # Advanced features
        "fetchLeverage": False,
        "setLeverage": False,
        "fetchFundingRate": False,
        "fetchFundingHistory": False,
        "fetchDeposits": False,
        "fetchWithdrawals": False,
        # Order types
        "createMarketOrder": True,
        "createLimitOrder": True,
        "createStopOrder": False,
        "createStopLimitOrder": False,
        "createStopLossOrder": False,
        "createTakeProfitOrder": False,
        # Trading features
        "fetchL2OrderBook": False,
        # Account features
        "fetchLedger": False,
        # API features
        "has": {
            "fetchOHLCV": False,
            "fetchOrderBook": False,
            "fetchTrades": False,
            "fetchPositions": False,
            "fetchLeverage": False,
            "setLeverage": False,
            "fetchFundingRate": False,
            "fetchFundingHistory": False,
            "fetchBalanceList": True,  # MockExchange supports balance list
            "deposit": True,  # MockExchange supports deposits
            "withdraw": True,  # MockExchange supports withdrawals
            "canExecuteOrder": True,  # MockExchange supports dry run
        },
    }

    # Production mode capabilities (CCXT)
    PROD_CAPABILITIES = {
        # Core trading
        "createOrder": True,
        "cancelOrder": True,
        "fetchOrder": True,
        "fetchOrders": True,
        "fetchOpenOrders": True,
        "fetchClosedOrders": True,
        "fetchMyTrades": True,
        # Account
        "fetchBalance": True,
        "fetchPositions": True,  # CCXT supports futures
        # Market data
        "fetchTicker": True,
        "fetchTickers": True,
        "fetchOHLCV": True,  # CCXT supports this
        "fetchOrderBook": True,  # CCXT supports this
        "fetchTrades": True,  # CCXT supports this
        # Metadata
        "loadMarkets": True,
        "fetchMarkets": True,
        # Advanced features
        "fetchLeverage": True,
        "setLeverage": True,
        "fetchFundingRate": True,
        "fetchFundingHistory": True,
        "fetchDeposits": True,
        "fetchWithdrawals": True,
        # Order types
        "createMarketOrder": True,
        "createLimitOrder": True,
        "createStopOrder": True,
        "createStopLimitOrder": True,
        "createStopLossOrder": True,
        "createTakeProfitOrder": True,
        # Trading features
        "fetchL2OrderBook": True,
        # Account features
        "fetchLedger": True,
        # API features
        "has": {
            "fetchOHLCV": True,
            "fetchOrderBook": True,
            "fetchTrades": True,
            "fetchPositions": True,
            "fetchLeverage": True,
            "setLeverage": True,
            "fetchFundingRate": True,
            "fetchFundingHistory": True,
        },
    }

    def __init__(self, mode: str):
        self.mode = mode
        self._capabilities = self._get_capabilities_for_mode(mode)

    def _get_capabilities_for_mode(self, mode: str) -> Dict[str, Any]:
        """Get capabilities for the given mode."""
        if mode == "paper":
            return self.PAPER_CAPABILITIES.copy()
        elif mode == "prod":
            return self.PROD_CAPABILITIES.copy()
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def has(self, feature: str) -> bool:
        """Check if a feature is supported.

        Determines whether a specific feature is available in the current mode.
        This method is used by the gateway to check feature availability before
        attempting to use them, enabling graceful degradation.

        The feature names follow CCXT conventions (e.g., 'fetchOHLCV', 'createOrder')
        and are case-sensitive. This method provides a simple boolean response
        for easy conditional logic in user code.

        Args:
            feature: The feature name to check (e.g., 'fetchOHLCV', 'createOrder')

        Returns:
            bool: True if the feature is supported, False otherwise

        Example:
            if capabilities.has('fetchOHLCV'):
                ohlcv = gateway.fetch_ohlcv('BTC/USDT', '1h')
            else:
                print('OHLCV not available in this mode')
        """
        top_level = self._capabilities.get(feature, False)
        if isinstance(top_level, bool) and top_level:
            return True
        nested_has = self._capabilities.get("has", {})
        return bool(nested_has.get(feature, False))
    def get_has_dict(self) -> Dict[str, bool]:
        """Get the CCXT-style 'has' dict."""
        # Return all capabilities, not just the nested 'has' dict
        has_dict = {}
        for key, value in self._capabilities.items():
            if key != "has" and isinstance(value, bool):
                has_dict[key] = value

        # Also include the nested 'has' dict if it exists
        nested_has = self._capabilities.get("has", {})
        has_dict.update(nested_has)

        return has_dict

    def get_all_capabilities(self) -> Dict[str, Any]:
        """Get all capabilities for the current mode."""
        return self._capabilities.copy()

    def is_supported(self, method_name: str) -> bool:
        """Check if a method is supported in the current mode."""
        # Map method names to capability keys
        method_to_capability = {
            "create_order": "createOrder",
            "cancel_order": "cancelOrder",
            "fetch_order": "fetchOrder",
            "fetch_orders": "fetchOrders",
            "fetch_open_orders": "fetchOpenOrders",
            "fetch_closed_orders": "fetchClosedOrders",
            "fetch_my_trades": "fetchMyTrades",
            "fetch_balance": "fetchBalance",
            "fetch_positions": "fetchPositions",
            "fetch_ticker": "fetchTicker",
            "fetch_tickers": "fetchTickers",
            "fetch_ohlcv": "fetchOHLCV",
            "fetch_order_book": "fetchOrderBook",
            "fetch_trades": "fetchTrades",
            "load_markets": "loadMarkets",
            "fetch_markets": "fetchMarkets",
            "fetch_leverage": "fetchLeverage",
            "set_leverage": "setLeverage",
            "fetch_funding_rate": "fetchFundingRate",
            "fetch_funding_history": "fetchFundingHistory",
        }

        capability_key = method_to_capability.get(method_name, method_name)
        return self.has(capability_key)

    def require_support(self, method_name: str) -> None:
        """Require that a method is supported, raise NotSupported if not."""
        if not self.is_supported(method_name):
            from .errors import raise_not_supported

            raise_not_supported(method_name, self.mode)


# Global capabilities instance
_capabilities: Dict[str, Capabilities] = {}


def get_capabilities(mode: str) -> Capabilities:
    """Get capabilities for the given mode.

    Args:
        mode: The mode string ("paper" or "prod")

    Returns:
        Capabilities: Capabilities instance for the mode
    """
    if mode not in _capabilities:
        _capabilities[mode] = Capabilities(mode)

    return _capabilities[mode]


def has_feature(feature: str, mode: str) -> bool:
    """Check if a feature is supported in the given mode.

    Args:
        feature: Feature name to check
        mode: The mode string ("paper" or "prod")

    Returns:
        bool: True if feature is supported
    """
    capabilities = get_capabilities(mode)
    return capabilities.has(feature)


def get_has_dict(mode: str) -> Dict[str, bool]:
    """Get the CCXT-style 'has' dict for the given mode.

    Args:
        mode: The mode string ("paper" or "prod")

    Returns:
        Dict[str, bool]: CCXT-style capabilities dictionary
    """
    capabilities = get_capabilities(mode)
    return capabilities.get_has_dict()


def require_support(method_name: str, mode: str) -> None:
    """Require that a method is supported in the given mode.

    Args:
        method_name: Name of the method requiring support
        mode: The mode string ("paper" or "prod")

    Raises:
        NotSupported: If the method is not supported in the mode
    """
    capabilities = get_capabilities(mode)
    capabilities.require_support(method_name)
