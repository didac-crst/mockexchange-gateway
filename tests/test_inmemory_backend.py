"""tests/test_inmemory_backend.py

Unit tests for the in-memory backend.

Focus
-----
Verify that minimal expected behaviors of `InMemoryBackend` hold:
    * Ticker seeding via `set_ticker` makes the symbol visible through the
      same interface path (`/tickers`) used by the higher-level gateway.

Why test this?
--------------
Catches accidental regressions if the internal storage structure changes
(e.g., renaming keys, altering list shape) which would silently break
gateway assumptions.
"""

from mockexchange_gateway.backends import InMemoryBackend


def test_inmemory_set_ticker():
    """Setting a ticker exposes it through the `/tickers` endpoint.

    Steps
    -----
    1. Create a fresh backend (isolated state).
    2. Seed an ETH/USDT ticker (price = 3000).
    3. Fetch all tickers through the public `get("/tickers")` path.
    4. Assert the seeded symbol is present.

    Rationale
    ---------
    We assert only the *presence* of the symbol, not on price fields, to keep
    the test resilient if additional metadata (e.g., volume) is added later.
    """
    be = InMemoryBackend()
    be.set_ticker("ETH/USDT", 3000)
    data = be.get("/tickers")
    assert any(row["symbol"] == "ETH/USDT" for row in data)
