"""adapters/mapping.py

Data mapping utilities for converting between MockExchange and CCXT formats.

This module handles the translation of data structures between MockExchange
and CCXT to ensure consistent API responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class DataMapper:
    """Data mapper for converting between MockExchange and CCXT formats.

    This class provides utilities for converting data structures between
    MockExchange's internal format and CCXT's standardized format. This
    ensures that users get consistent data structures regardless of which
    backend is being used.

    The data mapper is essential for maintaining the CCXT-compatible interface
    while working with different backend systems. It handles:
    - Ticker data conversion
    - Order information mapping
    - Balance structure normalization
    - Market metadata formatting
    - Timestamp and datetime conversions

    All conversion methods are static, making them easy to use throughout
    the codebase without needing to instantiate the class.

    The mapper follows CCXT conventions for field names and data types,
    ensuring compatibility with existing CCXT code and libraries.
    """

    @staticmethod
    def mockexchange_ticker_to_ccxt(ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MockExchange ticker to CCXT format.

        Transforms MockExchange ticker data into the standard CCXT ticker format.
        This ensures that users get consistent ticker data regardless of whether
        they're using paper mode (MockExchange) or production mode (CCXT).

        The conversion handles:
        - Field name mapping (e.g., MockExchange fields to CCXT fields)
        - Data type normalization
        - Missing field handling (sets None for unsupported fields)
        - Timestamp conversion to ISO format

        MockExchange provides a subset of ticker data compared to CCXT, so
        some fields are set to None to maintain the CCXT structure while
        being honest about data availability.

        Args:
            ticker_data: Raw ticker data from MockExchange API

        Returns:
            Dict[str, Any]: CCXT-formatted ticker data with all standard fields
        """
        return {
            "symbol": ticker_data.get("symbol"),
            "timestamp": ticker_data.get("timestamp"),
            "datetime": DataMapper._timestamp_to_datetime(ticker_data.get("timestamp")),
            "high": None,  # MockExchange doesn't provide high/low
            "low": None,
            "bid": ticker_data.get("bid"),
            "bidVolume": ticker_data.get("bid_volume"),
            "ask": ticker_data.get("ask"),
            "askVolume": ticker_data.get("ask_volume"),
            "vwap": None,
            "open": None,
            "close": ticker_data.get("last"),
            "last": ticker_data.get("last"),
            "previousClose": None,
            "change": None,
            "percentage": None,
            "average": None,
            "baseVolume": None,
            "quoteVolume": None,
            "info": ticker_data,
        }

    @staticmethod
    def mockexchange_order_to_ccxt(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MockExchange order to CCXT format.

        Maps MockExchange order statuses to CCXT standard statuses:
        - MockExchange 'new' -> CCXT 'open'
        - MockExchange 'partially_filled' -> CCXT 'partially_filled'
        - MockExchange 'filled' -> CCXT 'closed'
        - MockExchange 'canceled' -> CCXT 'canceled'
        - MockExchange 'rejected' -> CCXT 'rejected'
        - MockExchange 'expired' -> CCXT 'expired'
        """
        # Map MockExchange statuses to CCXT standard statuses
        status_mapping = {
            "new": "open",
            "partially_filled": "partially_filled",
            "filled": "closed",
            "canceled": "canceled",
            "rejected": "rejected",
            "expired": "expired",
            "partially_canceled": "canceled",
            "partially_rejected": "rejected",
            "partially_expired": "expired",
        }

        mockexchange_status = order_data.get("status")
        ccxt_status = (
            status_mapping.get(str(mockexchange_status), str(mockexchange_status))
            if mockexchange_status
            else "unknown"
        )

        return {
            "id": order_data.get("id"),
            "clientOrderId": None,
            "datetime": DataMapper._timestamp_to_datetime(order_data.get("created_at")),
            "timestamp": order_data.get("created_at"),
            "lastTradeTimestamp": order_data.get("updated_at"),
            "status": ccxt_status,  # Use mapped CCXT status
            "symbol": order_data.get("symbol"),
            "type": order_data.get("type"),
            "timeInForce": None,
            "postOnly": None,
            "side": order_data.get("side"),
            "price": order_data.get("price"),
            "stopPrice": None,
            "amount": order_data.get("amount"),
            "filled": order_data.get("filled"),
            "remaining": order_data.get("remaining"),
            "cost": order_data.get("cost"),
            "trades": None,
            "fee": None,
            "info": order_data,
        }

    @staticmethod
    def mockexchange_balance_to_ccxt(balance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MockExchange balance to CCXT format."""
        result = {
            "info": balance_data.get("info", {}),
            "timestamp": balance_data.get("timestamp"),
            "datetime": DataMapper._timestamp_to_datetime(balance_data.get("timestamp")),
            "free": {},
            "used": {},
            "total": {},
        }

        # Extract asset balances
        assets = balance_data.get("assets", [])
        for asset_data in assets:
            asset = asset_data.get("asset")
            if asset:
                result["free"][asset] = asset_data.get("free", 0.0)
                result["used"][asset] = asset_data.get("used", 0.0)
                result["total"][asset] = asset_data.get("total", 0.0)

        return result

    @staticmethod
    def mockexchange_market_to_ccxt(market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MockExchange market to CCXT format."""
        return {
            "id": market_data.get("symbol"),  # Use symbol as ID
            "symbol": market_data.get("symbol"),
            "base": market_data.get("base"),
            "quote": market_data.get("quote"),
            "baseId": market_data.get("base"),
            "quoteId": market_data.get("quote"),
            "active": market_data.get("active", True),
            "type": "spot",
            "spot": True,
            "margin": False,
            "swap": False,
            "future": False,
            "option": False,
            "contract": False,
            "linear": None,
            "inverse": None,
            "contractSize": None,
            "expiry": None,
            "expiryDatetime": None,
            "strike": None,
            "optionType": None,
            "settleType": None,
            "status": "trading" if market_data.get("active", True) else "closed",
            "precision": market_data.get("precision", {}),
            "limits": market_data.get("limits", {}),
            "info": market_data,
        }

    @staticmethod
    def ccxt_order_to_mockexchange(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CCXT order format to MockExchange format."""
        order_type = order_data.get("type")
        payload = {
            "symbol": order_data.get("symbol"),
            "type": order_type,
            "side": order_data.get("side"),
            "amount": order_data.get("amount"),
            "params": order_data.get("params", {}),
        }
        # MockExchange expects limit_price for limit orders
        if order_type == "limit":
            payload["limit_price"] = order_data.get("price")
        return payload

    @staticmethod
    def _timestamp_to_datetime(timestamp: Optional[int]) -> Optional[str]:
        """Convert timestamp to ISO datetime string."""
        if timestamp is None:
            return None

        # Convert milliseconds to seconds if needed
        if timestamp > 1e12:  # Likely milliseconds
            timestamp = int(timestamp / 1000)

        return datetime.fromtimestamp(timestamp).isoformat()

    @staticmethod
    def _datetime_to_timestamp(datetime_str: Optional[str]) -> Optional[int]:
        """Convert ISO datetime string to timestamp."""
        if datetime_str is None:
            return None

        try:
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)  # Return milliseconds
        except ValueError:
            return None

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Normalize symbol to standard format."""
        return symbol.upper().strip()

    @staticmethod
    def validate_order_params(params: Dict[str, Any]) -> None:
        """Validate order parameters."""
        required_fields = ["symbol", "type", "side", "amount"]

        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        if params["type"] not in ["market", "limit"]:
            raise ValueError(f"Invalid order type: {params['type']}")

        if params["side"] not in ["buy", "sell"]:
            raise ValueError(f"Invalid order side: {params['side']}")

        if params["type"] == "limit" and "price" not in params:
            raise ValueError("Price is required for limit orders")


class ResponseMapper:
    """Response mapper for handling different response formats."""

    @staticmethod
    def ensure_list_response(data: Any) -> List[Dict[str, Any]]:
        """Ensure response is a list of dictionaries."""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []

    @staticmethod
    def ensure_dict_response(data: Any) -> Dict[str, Any]:
        """Ensure response is a dictionary."""
        if isinstance(data, dict):
            return data
        else:
            return {"data": data}

    @staticmethod
    def extract_pagination_info(response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pagination information from response."""
        return {
            "limit": response.get("limit"),
            "since": response.get("since"),
            "until": response.get("until"),
        }
