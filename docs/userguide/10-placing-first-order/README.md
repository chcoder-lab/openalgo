# 10 - Placing Your First Order

## Introduction

This is the exciting part - placing your first order through OpenAlgo! We'll start with the Analyzer (sandbox testing) mode to practice safely, then show you how to go live.

## Before You Begin

Ensure you have:
- [ ] OpenAlgo running
- [ ] Logged into your broker
- [ ] API key generated
- [ ] Understand order types (review [Module 02](../02-key-concepts/README.md) if needed)

## Method 1: Using the Playground (Easiest)

The Playground is the best way to start - it's a visual interface to test orders.

### Step 1: Enable Analyzer Mode (Recommended for First Order)

1. Go to **Analyzer** page
2. Click **Enable Analyzer Mode**
3. You now have $100,000 sandbox capital to practice

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ ANALYZER MODE ACTIVE                                        │
│  Orders will NOT go to your real broker                         │
│  Sandbox Balance: $100,000                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Open Playground

Navigate to **Playground** in the sidebar.

### Step 3: Fill Order Details

```
┌─────────────────────────────────────────────────────────────────┐
│  Place Order                                                     │
│                                                                  │
│  Symbol:      [AAPL                    ]                        │
│  Exchange:    [EQUITY        ▾]                                 │
│  Action:      [BUY           ▾]                                 │
│  Quantity:    [100                     ]                        │
│  Price Type:  [MARKET        ▾]                                 │
│  Product:     [CNC           ▾]                                 │
│  Strategy:    [MyFirstOrder            ]                        │
│                                                                  │
│  [Place Order]                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Fill in:
| Field | Value | Explanation |
|-------|-------|-------------|
| Symbol | AAPL | Apple Inc. stock |
| Exchange | EQUITY | US Equity market |
| Action | BUY | We're buying shares |
| Quantity | 100 | Number of shares |
| Price Type | MARKET | Buy at current price |
| Product | CNC | Delivery/overnight position |
| Strategy | MyFirstOrder | Label for tracking |

### Step 4: Execute Order

1. Click **Place Order**
2. Wait for response
3. You should see:

```json
{
  "status": "success",
  "orderid": "230125000012345"
}
```

### Step 5: Verify Order

1. Go to **Order Book**
2. Find your order
3. Status should be "Complete" (for market orders)

4. Go to **Positions**
5. See your new AAPL position

Congratulations! You've placed your first order! 🎉

## Method 2: Using API (For Automation)

### Using cURL

```bash
curl -X POST http://127.0.0.1:5001/api/v1/placeorder \
  -H "Content-Type: application/json" \
  -d '{
    "apikey": "YOUR_API_KEY",
    "strategy": "CurlTest",
    "symbol": "AAPL",
    "exchange": "EQUITY",
    "action": "BUY",
    "quantity": "100",
    "pricetype": "MARKET",
    "product": "CNC"
  }'
```

### Using Python

```python
from openalgo import api

# Connect to OpenAlgo
client = api(
    api_key="YOUR_API_KEY",
    host="http://127.0.0.1:5001"
)

# Place order
response = client.place_order(
    symbol="AAPL",
    exchange="EQUITY",
    action="BUY",
    quantity=100,
    price_type="MARKET",
    product="CNC",
    strategy="PythonTest"
)

print(response)
# {'status': 'success', 'orderid': '230125000012345'}
```

## Understanding the Order Response

### Success Response

```json
{
  "status": "success",
  "orderid": "230125000012345"
}
```

| Field | Meaning |
|-------|---------|
| status | "success" = order accepted |
| orderid | Unique identifier from broker |

### Error Response

```json
{
  "status": "error",
  "message": "Insufficient margin"
}
```

Common error messages:
| Error | Cause | Solution |
|-------|-------|----------|
| Insufficient margin | Not enough funds | Reduce quantity or add funds |
| Invalid symbol | Symbol not found | Check symbol format |
| Market closed | Trading hours over | Wait for market to open |
| Invalid quantity | Wrong lot size | Use correct lot size |

## Order Flow Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Order Flow                                            │
│                                                                              │
│  1. You submit order                                                        │
│         │                                                                    │
│         ▼                                                                    │
│  2. OpenAlgo validates                                                      │
│         │                                                                    │
│         ├──→ Invalid? Return error                                          │
│         │                                                                    │
│         ▼                                                                    │
│  3. Check Analyzer Mode                                                     │
│         │                                                                    │
│         ├──→ ON?  Execute in sandbox (virtual)                              │
│         │                                                                    │
│         ▼                                                                    │
│  4. Check Order Mode                                                        │
│         │                                                                    │
│         ├──→ Semi-Auto? Queue in Action Center                              │
│         │                                                                    │
│         ▼                                                                    │
│  5. Send to Broker                                                          │
│         │                                                                    │
│         ▼                                                                    │
│  6. Broker executes                                                         │
│         │                                                                    │
│         ▼                                                                    │
│  7. Return order ID                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Practice Exercises

### Exercise 1: Market Buy Order

Place a market buy order:
- Symbol: AAPL
- Exchange: EQUITY
- Quantity: 50
- Product: CNC

### Exercise 2: Limit Buy Order

Place a limit order:
- Symbol: TSLA
- Exchange: EQUITY
- Action: BUY
- Quantity: 25
- Price Type: LIMIT
- Price: $200 (below current price)

Watch it appear as "Pending" in order book.

### Exercise 3: Sell Order

First, ensure you have a position from Exercise 1, then:
- Symbol: AAPL
- Exchange: EQUITY
- Action: SELL
- Quantity: 50
- Product: CNC

### Exercise 4: Exit Position

Use the Positions page:
1. Find your AAPL position
2. Click **Exit**
3. Watch it close

## Going Live (Real Orders)

Once comfortable with sandbox testing:

### Step 1: Disable Analyzer Mode

1. Go to **Analyzer** page
2. Click **Disable Analyzer Mode**
3. Confirm you want to trade with real money

### Step 2: Verify Broker Connection

- Check broker status is 🟢 Connected
- Verify available margin

### Step 3: Start Small

For your first real order:
- Use small quantity
- Choose liquid stocks (AAPL, TSLA, MSFT)
- Use MARKET orders (guaranteed execution)
- Use CNC for delivery/overnight positions

### Step 4: Place Real Order

Same process as before, but now:
- Orders go to real broker
- Real money at stake
- Real positions created

## Order Checklist

Before every order:

- [ ] Correct symbol?
- [ ] Correct exchange (EQUITY/OPTIONS/FUTURES)?
- [ ] BUY or SELL correct?
- [ ] Quantity correct?
- [ ] Price type appropriate?
- [ ] Sufficient margin available?
- [ ] Analyzer mode ON/OFF as intended?

## Common First-Order Mistakes

### Mistake 1: Wrong Exchange

**Problem**: Trying to buy AAPL options on EQUITY
**Solution**: Use OPTIONS exchange for options contracts

### Mistake 2: Wrong Lot Size

**Problem**: Buying 1000 AAPL options (check contract size)
**Solution**: Check contract size in Search page

### Mistake 3: Wrong product type for options

**Problem**: Using wrong product type for options
**Solution**: Use CNC for US options positions

### Mistake 4: Forgetting Strategy Name

**Problem**: Empty strategy field
**Solution**: Always name your strategy for tracking

## What's Next?

Now that you can place orders:

1. **Learn Order Types**: [Module 11](../11-order-types/README.md) - Understand all order types
2. **Try Smart Orders**: [Module 12](../12-smart-orders/README.md) - Position-aware orders
3. **Automate with TradingView**: [Module 16](../16-tradingview-integration/README.md)

---

**Previous**: [09 - API Key Management](../09-api-key-management/README.md)

**Next**: [11 - Order Types Explained](../11-order-types/README.md)
