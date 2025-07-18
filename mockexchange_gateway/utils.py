from __future__ import annotations
from typing import Iterable


def normalize_symbol(symbol: str) -> str:
    return symbol.upper()


def split_symbol(symbol: str) -> tuple[str, str]:
    base, quote = symbol.split("/")
    return base, quote


def ensure_set(iterable: Iterable[str]) -> set[str]:
    return set(iterable)
