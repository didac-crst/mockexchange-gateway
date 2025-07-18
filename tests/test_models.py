from mockexchange_gateway.models import Ticker


def test_ticker_model_alias():
    t = Ticker(symbol="BTC/USDT", timestamp=1, bidVolume=0.1)
    assert t.bid_volume == 0.1
