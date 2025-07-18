from mockexchange_gateway import MockExchangeGateway

gx = MockExchangeGateway(base_url="http://localhost:8000", api_key="dev-key")
markets = gx.load_markets()
print("Markets:", markets)

balance = gx.fetch_balance()
print("Balance keys:", list(balance.keys()))
