def test_load_markets(gateway):
    markets = gateway.load_markets()
    assert "BTC/USDT" in markets


def test_create_order_buy(gateway):
    order = gateway.create_order("BTC/USDT", "market", "buy", 0.002)
    assert order["status"] == "filled"
    assert order["filled"] == 0.002
