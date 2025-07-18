from mockexchange_gateway import MockExchangeGateway

gx = MockExchangeGateway()
orders = gx.fetch_open_orders()
print("Open orders:", orders)
