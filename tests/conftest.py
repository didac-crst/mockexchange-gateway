import pytest
from mockexchange_gateway.ccxt_like import MockExchangeGateway
from mockexchange_gateway.backends import InMemoryBackend


@pytest.fixture
def backend():
    be = InMemoryBackend()
    be.set_ticker("BTC/USDT", last=50000, bid=49990, ask=50010)
    return be


@pytest.fixture
def gateway(backend):
    return MockExchangeGateway(http_client=backend)
