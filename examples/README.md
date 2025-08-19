# MockX Gateway Examples

This directory contains comprehensive examples demonstrating how to use the MockX Gateway library.

## 🚀 Quick Start

```bash
# Test basic functionality (no external dependencies)
python examples/test_imports.py

# Run examples with MockExchange (requires MockExchange running)
python examples/basic_usage.py
python examples/place_market_order.py
python examples/list_open_orders.py
```

## 📚 Example Categories

### **🔧 Basic Setup & Configuration**
- **`test_imports.py`** - Verify installation and basic functionality
- **`basic_usage.py`** - Paper vs Production mode configuration
- **`error_handling.py`** - Handle NotSupported and other errors gracefully

### **📊 Market Data & Account**
- **`fetch_ticker.py`** - Get real-time price data
- **`fetch_balance.py`** - Check account balances
- **`load_markets.py`** - Discover available trading pairs

### **💼 Trading Operations**
- **`place_market_order.py`** - Place market orders
- **`list_open_orders.py`** - View pending orders

### **💰 Account & Balance**
- **`advanced_balance_operations.py`** - Balance list, deposits, withdrawals

### **📈 Advanced Features**
- **`capability_checking.py`** - Check feature availability before use
- **`context_manager.py`** - Use gateways with `with` statements
- **`production_mode.py`** - Real exchange integration (requires API keys)

## 🎯 Use Cases Covered

| Use Case | Example File | Description |
|----------|--------------|-------------|
| **Installation Test** | `test_imports.py` | Verify library works without external dependencies |
| **Paper Mode** | `basic_usage.py` | MockExchange for testing strategies |
| **Production Mode** | `production_mode.py` | Real exchange trading (requires API keys) |
| **Error Handling** | `error_handling.py` | Graceful handling of unsupported features |
| **Market Data** | `fetch_ticker.py` | Real-time price information |
| **Account Info** | `fetch_balance.py` | Account balance and positions |
| **Order Management** | `place_market_order.py` | Place and manage trading orders |
| **Advanced Balance** | `advanced_balance_operations.py` | Balance list, deposits, withdrawals |
| **Feature Detection** | `capability_checking.py` | Check what features are available |

## 🔑 Prerequisites

### **For Paper Mode Examples:**
- MockExchange running at `http://localhost:8000` (or your custom URL)
- No API keys required (uses default `dev-key`)

### **For Production Mode Examples:**
- Valid exchange API credentials (Binance, Coinbase, etc.)
- Exchange account with testnet/sandbox access (recommended)

## 🛠️ Running Examples

### **1. Test Installation**
```bash
python examples/test_imports.py
```

### **2. Paper Mode Examples**
```bash
# Start MockExchange first, then:
python examples/basic_usage.py
python examples/place_market_order.py
python examples/list_open_orders.py
```

### **3. Production Mode Examples**
```bash
# Set your API credentials first, then:
python examples/production_mode.py
```

## 📖 Example Output

### **Successful Paper Mode:**
```
=== Paper Mode Example ===
Gateway mode: Paper
Gateway capabilities: 15 features
Supports createOrder: True
Supports fetchOHLCV: False
Markets loaded: 10 trading pairs
Balance structure: ['info', 'timestamp', 'datetime', 'free', 'used', 'total']
```

### **Error Handling:**
```
=== Error Handling Example ===
✅ Feature supported: createOrder
❌ Feature not supported: fetchOHLCV
Error: fetchOHLCV not supported in paper mode (MockExchange backend)
```

## 🔧 Customization

### **Change MockExchange URL:**
```python
gateway = ExchangeFactory.create_paper_gateway(
    base_url="http://your-mockexchange-url:8000",
    api_key="your-api-key"
)
```

### **Use Different Exchange:**
```python
gateway = ExchangeFactory.create_prod_gateway(
    exchange_id="coinbase",  # or 'kraken', 'kucoin', etc.
    api_key="your-api-key",
    secret="your-secret",
    sandbox=True  # Use testnet
)
```

## 🚨 Troubleshooting

### **Connection Errors:**
- Ensure MockExchange is running
- Check the base URL in examples
- Verify network connectivity

### **Authentication Errors:**
- Check API key format
- Ensure API key has correct permissions
- Use sandbox/testnet for testing

### **NotSupported Errors:**
- Check `gateway.has` before using features
- Some features only work in production mode
- MockExchange has limited feature set

## 📝 Contributing Examples

When adding new examples:

1. **Follow naming convention**: `descriptive_name.py`
2. **Include docstring**: Explain what the example demonstrates
3. **Add error handling**: Show how to handle common errors
4. **Update this README**: Add new examples to the table above
5. **Test both modes**: Show paper and production when applicable
