from mockexchange_gateway import MockExchangeGateway

gx = MockExchangeGateway()
gx.load_markets()
order = gx.create_order("BTC/USDT", type="market", side="buy", amount=0.001)
print(order)
