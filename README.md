# MockExchange Gateway
Thin **CCXT-like** Python client for the `mockexchange_api` back-end. Provides a minimal surface for:
- Market data (tickers)
- Balance snapshots
- Order lifecycle (create, list, cancel, dry-run)
- A future‑proof structure to extend toward trades, websockets, and historical replay.

> **Status:** Alpha. The interface intentionally covers only what the other mockexchange components need right now; it will grow *incrementally*.

---

## ✨ Why this exists
You have:
- **`mockexchange-api`** – the REST back-end (order matching, persistence, tickers cache).
- **`mockexchange-deck`** – the Streamlit UI.
- **`mockexchange-gateway`** (this repo) – a *thin client* exposing CCXT-like method names so higher layers (strategies, backtests, scripts) remain swappable with real exchanges later.

Keep the client *dumb*: all authoritative logic stays server-side.

---

## 🧱 Install

```bash
pip install git+https://github.com/didac-crst/mockexchange-gateway.git
```

(Or add to `pyproject.toml` / `requirements.txt` as a VCS dependency.)

---

## 🚀 Quick Start

```python
from mockexchange_gateway import MockExchangeGateway

gx = MockExchangeGateway(base_url="http://localhost:8000", api_key="dev-key")
gx.load_markets()                                # populates internal symbol cache
print(gx.fetch_ticker("BTC/USDT"))               # single ticker
order = gx.create_order("BTC/USDT", "market", "buy", 0.001)
print(order)
print(gx.fetch_balance())
```

---

## 🗂️ Project Layout

```text
mockexchange_gateway/
├── mockexchange_gateway/
│   ├── __init__.py
│   ├── client.py                 ← Low-level HTTP client (session, auth, retries)
│   ├── ccxt_like.py              ← High-level CCXT-style facade
│   ├── models.py                 ← Pydantic models: Ticker, BalanceAsset, Order
│   ├── exceptions.py             ← Custom exception hierarchy
│   ├── utils.py                  ← Symbol & misc helpers
│   ├── config.py                 ← Defaults & env loader
│   ├── backends/                 ← Optional local / test backends
│   │   ├── __init__.py
│   │   ├── inmemory.py           ← In-memory backend (no HTTP) for tests
│   │   └── replay.py             ← (Future) historical / recorded replay
│   └── typing.py                 ← Protocols / shared type hints
├── examples/
│   ├── basic_usage.py
│   ├── place_market_order.py
│   └── list_open_orders.py
├── tests/
│   ├── __init__.py
│   ├── test_ccxt_like.py
│   ├── test_client.py
│   ├── test_models.py
│   └── test_inmemory_backend.py
├── pyproject.toml
├── README.md
└── .gitignore
```

---

## 🔌 CCXT-like Method Mapping

| Method (public) | HTTP endpoint | Purpose / Notes |
|-----------------|---------------|-----------------|
| `load_markets()` | `GET /tickers` | Populate symbol cache. |
| `fetch_markets()` | `GET /tickers` | Return list of basic market metadata. |
| `fetch_ticker(symbol)` | `GET /tickers/{symbol}` | Single latest ticker. |
| `fetch_tickers(symbols=None)` | `GET /tickers` | All tickers; optionally filter client-side. |
| `fetch_balance()` | `GET /balance` | Return CCXT-like balance dict (`free`, `used`, `total`). |
| `create_order(symbol, type, side, amount, price=None, params=None)` | `POST /orders` | Market or limit order. |
| `fetch_order(id, symbol=None)` | `GET /orders/{oid}` | Retrieve a single order. |
| `fetch_orders(symbol=None, status=None, side=None, tail=None)` | `GET /orders` | List/filter orders. |
| `fetch_open_orders(symbol=None)` | `GET /orders?status=open` | Convenience wrapper. |
| `cancel_order(id, symbol=None)` | `POST /orders/{oid}/cancel` | Cancel open order. |
| `can_execute_order(symbol, type, side, amount, price=None)` | `POST /orders/can_execute` | Dry-run balance / margin check. |
| *(future)* `fetch_my_trades(...)` | (not yet) | Add once trade fills endpoint exists. |

> The interface stops short of full CCXT breadth (no unified errors, no OHLCV, no leverage, no margins yet). Extend only when needed.

---

## 🧪 Testing

*Unit tests* mock or use the `InMemoryBackend`.  
Example (pytest fixture):

```python
from mockexchange_gateway.ccxt_like import MockExchangeGateway
from mockexchange_gateway.backends import InMemoryBackend

be = InMemoryBackend()
be.set_ticker("BTC/USDT", last=50000, bid=49990, ask=50010)
gx = MockExchangeGateway(http_client=be)
assert "BTC/USDT" in gx.load_markets()
```

Run:

```bash
pip install -e .[dev]
pytest
```

---

## ⚙️ Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `MOCKEXCHANGE_BASE_URL` | `http://localhost:8000` | API root URL |
| `MOCKEXCHANGE_API_KEY`  | *(none)* | Optional API key (sent as `x-api-key`) |
| `MOCKEXCHANGE_TIMEOUT`  | `10` | HTTP request timeout (seconds) |

Override per instance via constructor args or environment.

---

## 🧱 Design Principles

1. **Thin client** – no hidden business logic (matching, balances) duplicated client-side.  
2. **Deterministic models** – pydantic models validate & normalize all responses.  
3. **Progressive expansion** – only add surface actually required upstream.  
4. **Swap potential** – higher-layer code can later switch to real CCXT by adjusting import path.  
5. **Testability** – `InMemoryBackend` mimics `/tickers`, `/orders`, `/balance` without HTTP.

---

## 🛣️ Roadmap (Possible Next Steps)

- `fetch_my_trades` once `/trades` endpoint exists.
- Historical candle support (`fetch_ohlcv`) if server adds `/candles`.
- Async variant (`AsyncMockExchangeGateway`) via `httpx`.
- WebSocket streamer for live pushes (optional).
- CLI utilities: `mockx balance`, `mockx orders`.
- Replay backend for deterministic strategy backtests.

---

## 🗺️ Example Script (orders loop)

```python
import time
from mockexchange_gateway import MockExchangeGateway

gx = MockExchangeGateway()
gx.load_markets()

for _ in range(3):
    t = gx.fetch_ticker("BTC/USDT")
    print("Last:", t["last"])
    time.sleep(1)

order = gx.create_order("BTC/USDT", "market", "buy", 0.002)
print("Filled order:", order["id"], order["status"])
```

---

## 📦 Packaging / Dev Quick Start

```bash
git clone https://github.com/your-org/mockexchange_gateway.git
cd mockexchange_gateway
pip install -e .[dev]
pytest
```

Publish (when ready):

```bash
python -m build
twine upload dist/*
```

---

## 📄 License

MIT (see `LICENSE`).

---

## 🙋 Support / Contributions

PRs welcome: keep scope minimal, include tests & type hints.  
Open issues for any endpoint shape drift between client and `mockexchange_api`.

---

*Happy hacking.*
