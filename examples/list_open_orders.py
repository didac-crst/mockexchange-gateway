"""examples/list_open_orders.py

Example: retrieving open orders.

Rationale
---------
Separated from `basic_usage.py` to keep each example *single-purpose*:
    * Easier for new users to locate a relevant snippet.
    * Reduces cognitive load (no unrelated balance / ticker noise).

Assumptions
-----------
* The `mockexchange_api` server is running and accessible at the default
  base URL (`http://localhost:8000`).
* Markets have been loaded previously or the server endpoints function
  without requiring an explicit preload (the gateway will call the
  orders endpoint directly).
"""

from mockexchange_gateway import MockExchangeGateway

# Using defaults: base_url and api_key resolved via environment or hardcoded defaults.
gx = MockExchangeGateway()

# Retrieve currently open orders. If none exist, expect an empty list.
# This mirrors CCXT's 'fetch_open_orders' semantics.
orders = gx.fetch_open_orders()
print("Open orders:", orders)
