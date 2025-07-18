"""examples/replay_usage.py

Example: deterministic market data playback using `ReplayBackend`.

Purpose
-------
Demonstrates how to:
    1. Construct a `ReplayBackend` from an in-memory events dictionary.
    2. Inject it into `MockExchangeGateway` (dependency inversion).
    3. Manually advance replay time and observe ticker / balance changes.
    4. Place orders during replay with deterministic pricing.

Why separate from other examples?
---------------------------------
Replay is a *testing / research* concern, distinct from live API usage.
Keeping it isolated prevents confusing newcomers who only need the basic
`HttpClient` path.

Run
---
Execute directly (after installing dev deps):

    python examples/replay_usage.py
"""

from mockexchange_gateway.ccxt_like import MockExchangeGateway
from mockexchange_gateway.backends.replay import ReplayBackend


# -----------------------------------------------------------------------------
# 1. Define a tiny synthetic event stream.
#    Keep it short so example output is easy to read.
# -----------------------------------------------------------------------------
events = {
    "tickers": [
        {"timestamp": 1710000000000, "symbol": "BTC/USDT", "last": 50000, "bid": 49990, "ask": 50010},
        {"timestamp": 1710000000500, "symbol": "BTC/USDT", "last": 50010, "bid": 50000, "ask": 50020},
        {"timestamp": 1710000001000, "symbol": "BTC/USDT", "last": 50025, "bid": 50015, "ask": 50035},
        {"timestamp": 1710000001500, "symbol": "BTC/USDT", "last": 50012, "bid": 50002, "ask": 50022},
    ],
    "initial_balances": {
        "USDT": {"free": 10_000.0, "used": 0.0},
        "BTC": {"free": 0.0, "used": 0.0},
    },
}

# -----------------------------------------------------------------------------
# 2. Build a replay backend.
#    auto_advance=False gives explicit control; set True for auto stepping.
# -----------------------------------------------------------------------------
backend = ReplayBackend(events, auto_advance=False, strict=True)

# -----------------------------------------------------------------------------
# 3. Inject into the gateway instead of a real HTTP client.
# -----------------------------------------------------------------------------
gx = MockExchangeGateway(http_client=backend)

# Helper function for pretty printing:
def _print_ticker(tag: str):
    t = gx.fetch_ticker("BTC/USDT")
    print(f"{tag} @ {t['timestamp']}: last={t['last']} bid={t['bid']} ask={t['ask']}")


print("=== Initial snapshot ===")
_print_ticker("T0")

# -----------------------------------------------------------------------------
# 4. Advance replay time step-by-step.
# -----------------------------------------------------------------------------
backend.advance(steps=1)
_print_ticker("T1")

backend.advance(steps=1)
_print_ticker("T2")

# -----------------------------------------------------------------------------
# 5. Place an order at the *current* replay price.
# -----------------------------------------------------------------------------
order = gx.create_order("BTC/USDT", type="market", side="buy", amount=0.01)
print("Order filled:", order)

# -----------------------------------------------------------------------------
# 6. Show updated balance (BTC should now be credited).
# -----------------------------------------------------------------------------
balance = gx.fetch_balance()
print("BTC balance after buy:", balance.get("BTC"))
print("USDT balance after buy:", balance.get("USDT"))

# -----------------------------------------------------------------------------
# 7. Jump directly to a future timestamp (beyond last tick -> clamps).
# -----------------------------------------------------------------------------
backend.advance(to_timestamp=1710000002000)
_print_ticker("T-final (clamped)")

# -----------------------------------------------------------------------------
# 8. Dry-run insufficient funds scenario (exaggerated amount).
# -----------------------------------------------------------------------------
can = backend.post("/orders/can_execute", json={"symbol": "BTC/USDT", "side": "buy", "type": "market", "amount": 999})
print("Can execute huge buy?", can)

print("=== Replay example complete ===")
