"""tests/conftest.py

Pytest configuration & reusable fixtures.

Why fixtures here?
------------------
Placing shared fixtures in `conftest.py` (auto-discovered by pytest) lets
all test modules import them implicitly without repetitive import lines.
This keeps individual test files lean and focused on assertions.

Provided Fixtures
-----------------
backend : InMemoryBackend
    An isolated in-memory mock exchange populated with a BTC/USDT ticker.
gateway : MockExchangeGateway
    Gateway wired to the in-memory backend (no real HTTP).
"""

import pytest
from mockexchange_gateway.ccxt_like import MockExchangeGateway
from mockexchange_gateway.backends import InMemoryBackend


@pytest.fixture
def backend():
    """Return a pre-seeded in-memory backend.

    Seeding a deterministic ticker (BTC/USDT @ 50_000) ensures:
        * Order cost calculations are predictable (cost = amount * 50_000).
        * Tests remain stable across runs (no random price variance).
    We also set bid/ask explicitly to exercise code that might rely on them.
    """
    be = InMemoryBackend()
    be.set_ticker("BTC/USDT", last=50000, bid=49990, ask=50010)
    return be


@pytest.fixture
def gateway(backend):
    """Gateway fixture bound to the in-memory backend.

    Dependency injection via `http_client=backend` avoids making real network
    calls and speeds up tests dramatically. Any test receiving `gateway`
    automatically also benefits from the pre-seeded ticker in `backend`.
    """
    return MockExchangeGateway(http_client=backend)
