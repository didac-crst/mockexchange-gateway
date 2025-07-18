"""examples/place_market_order.py

Example: placing a simple market buy order.

Purpose
-------
Show the minimal sequence to:
    1. Initialize the gateway client
    2. Load available markets
    3. Submit a market order
    4. Inspect the normalized order response

Why a dedicated file?
---------------------
Keeping *one behavior per example* makes it easier for users to grep
or skim the `examples/` directory and quickly find the scenario they need.
"""

from mockexchange_gateway import MockExchangeGateway

# Instantiate with default configuration (base_url can be overridden via env
# or by passing it explicitly). For concise examples we omit the api_key;
# in authenticated setups you would pass api_key="...".
gx = MockExchangeGateway()

# Ensure symbol cache is populated. While some methods don't strictly need
# this (server endpoints can still function), mirroring the CCXT usage
# pattern reinforces consistency and catches symbol availability issues early.
gx.load_markets()

# Create a market BUY order for 0.001 BTC against USDT.
# Price is determined server-side (latest ticker). We intentionally avoid
# extra params here to keep the example focused and readable.
order = gx.create_order("BTC/USDT", type="market", side="buy", amount=0.001)

# Print the normalized order dict. In real code you'd persist, log, or
# feed this into strategy state machines.
print(order)
