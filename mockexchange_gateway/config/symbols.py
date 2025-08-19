"""config/symbols.py

Symbol mapping and normalization for MockX Gateway.

This module handles:
- Symbol format conversion between MockExchange and CCXT
- Symbol validation
- Symbol mapping configuration
"""

import json
from pathlib import Path
from typing import Dict, Optional, Set


class SymbolMapper:
    """Symbol mapping and normalization utility.

    This class handles symbol format conversion and validation between different
    exchange systems. It ensures that trading symbols are properly formatted
    and consistent across MockExchange and CCXT backends.

    The symbol mapper serves several purposes:
    1. **Format Normalization**: Converts symbols to the correct format for each backend
    2. **Custom Mappings**: Handles cases where different systems use different symbol formats
    3. **Validation**: Ensures symbols are properly formatted before use
    4. **Flexibility**: Allows custom symbol mappings via configuration files

    Symbol formats can vary between exchanges (e.g., "BTC/USDT" vs "BTCUSDT"),
    and this mapper ensures that users can work with consistent symbol formats
    regardless of the underlying backend.

    The mapper supports both automatic format detection and custom mapping files,
    providing flexibility for different use cases and exchange requirements.
    """

    def __init__(self, mapping_file: Optional[str] = None):
        self.mappings = self._load_mappings(mapping_file)
        self._normalized_symbols: Set[str] = set()

    def _load_mappings(self, mapping_file: Optional[str]) -> Dict[str, str]:
        """Load symbol mappings from file or use defaults."""
        if mapping_file and Path(mapping_file).exists():
            with open(mapping_file, "r") as f:
                raw = json.load(f)
                if not isinstance(raw, dict):
                    raise ValueError("Symbol mapping file must contain a JSON object of mappings")
                return {str(k).upper(): str(v).upper() for k, v in raw.items()}
        # Default mappings (MockExchange format -> CCXT format)
        return {
            # Add any specific mappings here if needed
            # "BTCUSDT": "BTC/USDT",
            # "ETHUSDT": "ETH/USDT",
        }

    def normalize_symbol(self, symbol: str, mode: str) -> str:
        """Normalize symbol to canonical format for the given mode."""
        # Remove any whitespace and convert to uppercase
        symbol = symbol.strip().upper()

        # Apply any custom mappings
        if symbol in self.mappings:
            symbol = self.mappings[symbol]

        # Ensure proper format based on mode
        if mode == "paper":
            return self._to_mockexchange_format(symbol)
        else:
            return self._to_ccxt_format(symbol)

    def _to_mockexchange_format(self, symbol: str) -> str:
        """Convert symbol to MockExchange format."""
        # MockExchange typically uses BTC/USDT format
        # If it's already in this format, return as is
        if "/" in symbol:
            return symbol

        # Try to convert from BTCUSDT to BTC/USDT
        # This is a simple heuristic - you might need more sophisticated logic
        if len(symbol) >= 6:
            # Common quote currencies
            quote_currencies = [
                "USDT",
                "USD",
                "BTC",
                "ETH",
                "BNB",
                "ADA",
                "DOT",
                "LINK",
            ]

            for quote in quote_currencies:
                if symbol.endswith(quote):
                    base = symbol[: -len(quote)]
                    if base:
                        return f"{base}/{quote}"

        # If we can't determine the format, return as is
        return symbol

    def _to_ccxt_format(self, symbol: str) -> str:
        """Convert symbol to CCXT format."""
        # CCXT typically uses BTC/USDT format
        # If it's already in this format, return as is
        if "/" in symbol:
            return symbol

        # Try to convert from BTCUSDT to BTC/USDT
        # Same logic as MockExchange for now
        return self._to_mockexchange_format(symbol)

    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol is in the correct format."""
        if not symbol:
            return False

        # Basic validation: should contain a separator
        if "/" not in symbol:
            return False

        # Should have both base and quote
        parts = symbol.split("/")
        if len(parts) != 2:
            return False

        base, quote = parts
        if not base or not quote:
            return False

        return True

    def get_supported_symbols(self, mode: str) -> Set[str]:
        """Get set of supported symbols for the given mode."""
        # This would typically be populated from the exchange
        # For now, return an empty set
        return set()

    def add_symbol_mapping(self, from_symbol: str, to_symbol: str) -> None:
        """Add a custom symbol mapping."""
        self.mappings[from_symbol.upper()] = to_symbol.upper()

    def remove_symbol_mapping(self, symbol: str) -> None:
        """Remove a symbol mapping."""
        symbol = symbol.upper()
        if symbol in self.mappings:
            del self.mappings[symbol]


# Global symbol mapper instance
_symbol_mapper: Optional[SymbolMapper] = None


def get_symbol_mapper() -> SymbolMapper:
    """Get the global symbol mapper instance."""
    global _symbol_mapper

    if _symbol_mapper is None:
        # No longer using environment variables for configuration
        # Symbol mapping can be configured explicitly if needed
        _symbol_mapper = SymbolMapper(None)

    return _symbol_mapper


def normalize_symbol(symbol: str, mode: str) -> str:
    """Normalize a symbol for the given mode."""
    mapper = get_symbol_mapper()
    return mapper.normalize_symbol(symbol, mode)


def validate_symbol(symbol: str) -> bool:
    """Validate if a symbol is in the correct format."""
    mapper = get_symbol_mapper()
    return mapper.validate_symbol(symbol)
