# 14 - Positions & Holdings

## Introduction

Understanding the difference between positions and holdings is fundamental to trading. This guide explains both concepts and how to manage them in OpenAlgo.

## Positions vs Holdings

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Positions vs Holdings                                      │
│                                                                              │
│  POSITIONS                              HOLDINGS                            │
│  ──────────                             ────────                            │
│                                                                              │
│  • Day trades (CNC)                    • Long-term trades (CNC)             │
│  • Options/Futures positions           • Stocks in your account             │
│  • Active today                        • Long-term investments              │
│  • Must close or convert               • No expiry (equity)                 │
│  • Mark-to-market P&L                  • Dividend eligible                  │
│                                                                              │
│  Example:                               Example:                            │
│  Bought AAPL CNC today                 Bought AAPL CNC last month           │
│  → Shows in Positions                  → Shows in Holdings                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Understanding Positions

### What is a Position?

A position is an open trade that hasn't been closed yet:
- Equity trades (CNC product)
- Futures and Options trades
- Any trade that's "open" for the day

### Position Data Fields

| Field | Description |
|-------|-------------|
| Symbol | Trading symbol (e.g., AAPL) |
| Exchange | EQUITY, OPTIONS, FUTURES, etc. |
| Product | CNC |
| Quantity | Number of shares/lots (+ for long, - for short) |
| Average Price | Your entry price |
| LTP | Last Traded Price |
| P&L | Unrealized profit/loss |
| Day's Change | Change since market open |

### Position Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Your Positions                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Symbol  │ Qty   │ Avg Price │  LTP   │   P&L   │ Product │ Exchange       │
│──────────│───────│───────────│────────│─────────│─────────│────────────────│
│  AAPL    │ +100  │ $185.00   │ $190.00│ +$500   │ CNC     │ EQUITY         │
│  TSLA    │ -50   │ $250.00   │ $240.00│ +$500   │ CNC     │ EQUITY         │
│  /ES     │ +1    │ $5150.00  │ $5165.00│ +$750  │ CNC     │ FUTURES        │
└─────────────────────────────────────────────────────────────────────────────┘

Total Unrealized P&L: +$1,750
```

### Reading Position Quantity

| Quantity | Meaning |
|----------|---------|
| +100 | Long 100 shares (bought) |
| -100 | Short 100 shares (sold) |
| 0 | No position (flat) |

## Understanding Holdings

### What are Holdings?

Holdings are stocks you own in your brokerage account:
- Purchased using CNC product
- Settled after T+1 day
- No expiry
- Eligible for dividends and corporate actions

### Holdings Data Fields

| Field | Description |
|-------|-------------|
| Symbol | Stock symbol |
| Quantity | Number of shares owned |
| Average Price | Your average cost |
| LTP | Current market price |
| Current Value | Qty × LTP |
| P&L | Total profit/loss |
| P&L % | Percentage return |

### Holdings Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Your Holdings                                        Total: $52,500        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Symbol  │ Qty  │ Avg Price │  LTP    │ Value    │  P&L    │ P&L %         │
│──────────│──────│───────────│─────────│──────────│─────────│───────────────│
│  AAPL    │ 100  │ $150.00   │ $165.00 │ $16,500  │+$1,500  │ +10.0%        │
│  MSFT    │ 50   │ $380.00   │ $408.00 │ $20,400  │+$1,400  │ +7.4%         │
│  TSLA    │ 25   │ $220.00   │ $244.00 │ $6,100   │+$600    │ +10.9%        │
│  NVDA    │ 10   │ $800.00   │ $780.00 │ $7,800   │-$200    │ -2.5%         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Viewing in OpenAlgo

### Positions Page

Navigate to **Positions** in sidebar:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Positions                                        [Refresh] [Close All]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Filters: [All Products ▾]  [All Exchanges ▾]                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  AAPL    EQUITY    +100    CNC                                     │    │
│  │  Avg: $185.00    LTP: $190.00    P&L: +$500         [Exit]         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Total P&L: +$1,750                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Holdings Page

Navigate to **Holdings** in sidebar:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Holdings                                         [Refresh] [Download]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Portfolio Value: $52,500                                                   │
│  Total Investment: $47,500                                                  │
│  Total P&L: +$5,000 (+10.5%)                                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Apple Inc. (AAPL)                                                 │    │
│  │  100 shares @ $150.00 avg                                         │    │
│  │  Current: $16,500    P&L: +$1,500 (+10%)            [Sell]         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Position Operations

### Closing a Position

**Method 1: UI Button**
1. Go to Positions page
2. Find the position
3. Click **Exit** button
4. Order placed at market price

**Method 2: API**
```json
{
  "apikey": "your-key",
  "strategy": "ManualExit",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "SELL",
  "quantity": "100",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Closing All Positions

**Method 1: UI**
1. Go to Positions page
2. Click **Close All** button
3. Confirm action
4. All positions squared off

**Method 2: API**
```
POST /api/v1/closeallpositions
{
  "apikey": "your-key",
  "strategy": "SquareOff"
}
```

### Modifying Position Size

```python
# Increase position
client.place_order(
    symbol="AAPL",
    action="BUY",
    quantity=50,  # Add 50 more
    ...
)

# Decrease position
client.place_order(
    symbol="AAPL",
    action="SELL",
    quantity=30,  # Reduce by 30
    ...
)
```

## API Endpoints

### Get Positions

```
POST /api/v1/positions
{
  "apikey": "your-key"
}
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "symbol": "AAPL",
      "exchange": "EQUITY",
      "product": "CNC",
      "quantity": 100,
      "average_price": 185.00,
      "ltp": 190.00,
      "pnl": 500.00
    }
  ]
}
```

### Get Holdings

```
POST /api/v1/holdings
{
  "apikey": "your-key"
}
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "symbol": "AAPL",
      "exchange": "EQUITY",
      "quantity": 100,
      "average_price": 150.00,
      "ltp": 165.00,
      "pnl": 1500.00,
      "pnl_percent": 10.0
    }
  ]
}
```

### Get Open Position (Specific)

```
POST /api/v1/openposition
{
  "apikey": "your-key",
  "strategy": "MyStrategy",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "product": "CNC"
}
```

## P&L Calculations

### Position P&L (Unrealized)

```
For LONG positions:
P&L = (LTP - Average Price) × Quantity

For SHORT positions:
P&L = (Average Price - LTP) × Quantity

Example (Long 100 AAPL):
Average: $185, LTP: $190
P&L = (190 - 185) × 100 = +$500
```

### Holdings P&L

```
P&L = (Current Price - Average Cost) × Quantity

P&L % = ((Current Price - Average Cost) / Average Cost) × 100

Example (100 AAPL):
Average: $150, Current: $165
P&L = (165 - 150) × 100 = +$1,500
P&L % = ((165 - 150) / 150) × 100 = +10%
```

## Auto Square-Off (Day Trades)

Day trade positions may be automatically squared off by your broker:

| Segment | Auto Square-Off Time (ET) |
|---------|--------------------------|
| Equity | 3:55 PM |
| Options | 3:55 PM |
| Futures | 3:55 PM |

**Tip**: Close positions yourself before auto square-off for better prices.

## Converting Positions

### Product Conversion

Convert position product type:
- Must be done before square-off time
- Additional margin may be required
- Check broker-specific rules

### Product Conversion API

```
POST /api/v1/convertposition
{
  "apikey": "your-key",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "quantity": "100",
  "from_product": "CNC",
  "to_product": "CNC"
}
```

## Best Practices

### Position Management

1. **Set stop-losses** for all positions
2. **Monitor margin** to avoid forced liquidation
3. **Close before auto square-off** when possible
4. **Review positions** at start and end of day

### Holdings Management

1. **Diversify** across sectors
2. **Review periodically** (quarterly)
3. **Rebalance** when needed
4. **Track corporate actions** (dividends, splits)

---

**Previous**: [13 - Basket Orders](../13-basket-orders/README.md)

**Next**: [15 - Analyzer Mode (Sandbox Testing)](../15-analyzer-mode/README.md)
