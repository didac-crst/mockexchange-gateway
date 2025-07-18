"""tests/test_models.py

Tests for the pydantic data models.

Purpose
-------
Validate that field aliasing and basic normalization behave as expected.
Catching alias regressions early prevents subtle downstream bugs where
callers rely on snake_case attributes while the API still emits camelCase.

Scope
-----
We keep model tests *surgical*:
    * Only assert on transformations / behaviors we intentionally provide.
    * Avoid duplicating pydantic's own responsibilities (e.g., type coercion)
      unless we layer custom validators later.
"""

from mockexchange_gateway.models import Ticker


def test_ticker_model_alias():
    """`bidVolume` (camelCase) should map to `bid_volume` (snake_case).

    Steps
    -----
    1. Instantiate `Ticker` using the API-style field name `bidVolume`.
    2. Assert the snake_case attribute `bid_volume` is populated.

    Why this matters
    ----------------
    Application code uses snake_case consistently. If alias mapping breaks,
    silent `None` values could propagate into analytics or UI layers.
    """
    t = Ticker(symbol="BTC/USDT", timestamp=1, bidVolume=0.1)
    assert t.bid_volume == 0.1
