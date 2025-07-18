"""tests/test_ccxt_like.py

Tests for the high-level CCXT-like facade (`MockExchangeGateway`).

Philosophy
----------
Keep unit tests *narrow*:
    * Each test validates one behavior.
    * Avoid asserting on incidental fields (e.g. timestamps) to reduce brittleness.
    * Use fixtures from `conftest.py` for DRY setup (gateway with seeded ticker).

Why only a couple of tests here?
--------------------------------
This file targets *facade wiring correctness* (markets caching & order creation).
Deeper behaviors (price math, balance updates) belong in dedicated tests if / when
logic moves client-side. Currently, that logic lives in the in-memory backend
and can be covered separately.
"""


def test_load_markets(gateway):
    """Gateway loads symbols and caches them.

    We assert only the presence of a known seeded symbol ("BTC/USDT") rather than
    the *entire* list; this keeps the test resilient if more symbols are added later.
    """
    markets = gateway.load_markets()
    assert "BTC/USDT" in markets  # Ensures symbol cache populated.


def test_create_order_buy(gateway):
    """Creating a market BUY order yields an immediately filled order.

    Assertions:
        * status == 'filled' (in-memory backend fills instantly by design)
        * filled amount matches requested amount (no partial fills modeled)
    """
    order = gateway.create_order("BTC/USDT", "market", "buy", 0.002)
    assert order["status"] == "filled"
    assert order["filled"] == 0.002
