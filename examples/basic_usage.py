"""examples/basic_usage.py

Minimal example demonstrating core usage of the gateway client.

Why this example?
-----------------
* Serves as a **smoke test** you can run manually to verify connectivity
  and config (base URL, API key) without diving into test suites.
* Provides copy‑paste starter code for new users reading the README.

Keep examples **short and linear** so they're easy to scan. More elaborate
scenarios (order loops, backtesting) belong in separate example scripts.
"""

from mockexchange_gateway import MockExchangeGateway

# Instantiate the gateway.
# We explicitly pass both base_url and api_key to avoid relying on env vars
# (examples should be explicit so users see required configuration).
gx = MockExchangeGateway(base_url="http://localhost:8000", api_key="dev-key")

# Load market symbols (cached internally after the first call). This mirrors
# the CCXT pattern while keeping network chatter minimal afterwards.
markets = gx.load_markets()
print("Markets:", markets)

# Fetch current balance snapshot. We only print the keys here to keep
# output concise; users can explore the full dict in an interactive shell.
balance = gx.fetch_balance()
print("Balance keys:", list(balance.keys()))
