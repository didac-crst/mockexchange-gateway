from mockexchange_gateway.backends import InMemoryBackend


def test_inmemory_set_ticker():
    be = InMemoryBackend()
    be.set_ticker("ETH/USDT", 3000)
    data = be.get("/tickers")
    assert any(row["symbol"] == "ETH/USDT" for row in data)
