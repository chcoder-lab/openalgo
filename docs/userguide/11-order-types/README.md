# 11 - Order Types Explained

## Introduction

Understanding order types is essential for effective trading. Each order type has specific use cases, advantages, and limitations.

## Order Types Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Order Types Hierarchy                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        MARKET ORDER                                  │   │
│  │           Execute immediately at best available price                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        LIMIT ORDER                                   │   │
│  │           Execute only at specified price or better                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      STOP-LOSS ORDER (SL)                           │   │
│  │       Triggers limit order when price reaches stop price            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   STOP-LOSS MARKET ORDER (SL-M)                     │   │
│  │       Triggers market order when price reaches stop price           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Market Order (MARKET)

### What It Does

Executes immediately at the current best available price.

### Example

```
Stock: AAPL
Current Price: $150.50
You place: MARKET BUY 100 shares

Result: You get 100 shares at approximately $150.50
(Actual price may vary slightly based on market)
```

### When to Use

| Use When | Don't Use When |
|----------|----------------|
| Need immediate execution | Price precision matters |
| Trading liquid stocks | Stock is thinly traded |
| News-based trading | Large order size |
| Exiting positions quickly | Volatile market conditions |

### Pros and Cons

| Pros | Cons |
|------|------|
| Guaranteed execution | No price control |
| Simple to use | May get worse price |
| Fast | Slippage in volatile markets |

### OpenAlgo API

```json
{
  "apikey": "your-key",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "100",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## Limit Order (LIMIT)

### What It Does

Executes only at your specified price or better.
- BUY LIMIT: Executes at your price or lower
- SELL LIMIT: Executes at your price or higher

### Example

```
Stock: AAPL
Current Price: $150
You place: LIMIT BUY 100 at $148

Scenario 1: Price drops to $148
Result: Order executes at $148 ✓

Scenario 2: Price stays above $148
Result: Order remains pending

Scenario 3: Price drops to $145
Result: Order executes at $148 (or better at $145)
```

### When to Use

| Use When | Don't Use When |
|----------|----------------|
| Want specific price | Need immediate execution |
| Buying dips | Fast-moving markets |
| Selling rallies | May miss opportunity |
| Large orders | News-based trading |

### Pros and Cons

| Pros | Cons |
|------|------|
| Price control | May not execute |
| No slippage | Order may expire |
| Better average price | Requires price monitoring |

### OpenAlgo API

```json
{
  "apikey": "your-key",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "100",
  "pricetype": "LIMIT",
  "price": "148",
  "product": "CNC"
}
```

## Stop-Loss Order (SL)

### What It Does

Combines a trigger price and a limit price:
1. Order stays dormant until trigger price is reached
2. Once triggered, becomes a limit order

### Example

```
You own: AAPL at $150
Current Price: $150
You place: SL SELL at Trigger $145, Limit $144

Price Movement:
$150 → $148 → $146 → $145 (TRIGGERED!)
                       ↓
           Limit sell order at $144 placed
                       ↓
           Executes at $144 or better
```

### When to Use

| Use When | Risk |
|----------|------|
| Protecting profits | May not execute if price gaps |
| Limiting losses | Requires two prices |
| Position management | Can be triggered by volatility |

### Trigger vs Limit Price

```
BUY Stop-Loss (for short positions):
  Trigger Price: Price that activates the order (higher)
  Limit Price: Maximum price you'll pay (equal or higher)

SELL Stop-Loss (for long positions):
  Trigger Price: Price that activates the order (lower)
  Limit Price: Minimum price you'll accept (equal or lower)
```

### OpenAlgo API

```json
{
  "apikey": "your-key",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "SELL",
  "quantity": "100",
  "pricetype": "SL",
  "price": "144",
  "trigger_price": "145",
  "product": "CNC"
}
```

## Stop-Loss Market Order (SL-M)

### What It Does

Triggers a market order when trigger price is reached:
1. Order stays dormant until trigger price hit
2. Once triggered, becomes a market order (guaranteed execution)

### Example

```
You own: AAPL at $150
Current Price: $150
You place: SL-M SELL at Trigger $145

Price Movement:
$150 → $148 → $146 → $145 (TRIGGERED!)
                       ↓
           Market sell order placed
                       ↓
           Executes immediately at market price
           (Could be $144, $143, or $146)
```

### When to Use

| Use When | Risk |
|----------|------|
| Must exit no matter what | Slippage in volatile markets |
| Gap down protection | May get worse price |
| Simpler than SL | No price control after trigger |

### SL vs SL-M Comparison

| Aspect | SL | SL-M |
|--------|----|----|
| Execution | Limit (may not fill) | Market (always fills) |
| Price control | Yes | No |
| Gap protection | Poor (may not fill) | Better (will fill) |
| Complexity | Two prices needed | One trigger price |
| Best for | Normal markets | Gap protection |

### OpenAlgo API

```json
{
  "apikey": "your-key",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "SELL",
  "quantity": "100",
  "pricetype": "SL-M",
  "trigger_price": "145",
  "product": "CNC"
}
```

## Price Type Reference

| Price Type | Parameters Needed | Use Case |
|------------|-------------------|----------|
| MARKET | None | Immediate execution |
| LIMIT | price | Specific price entry/exit |
| SL | price, trigger_price | Stop-loss with limit |
| SL-M | trigger_price | Stop-loss with market |

## Product Types

### CNC (Cash and Carry)

- Standard product type for US brokers
- Used for all positions: equities, options, and futures
- For delivery and overnight positions
- No auto square-off
- Stocks settle to your account

### MIS (Margin Intraday Square-off)

- For intraday trading (Indian brokers)
- Auto-closes before market end
- Higher leverage available
- Lower margin required

### NRML (Normal)

- For overnight F&O positions (Indian brokers)
- No auto square-off (within expiry)
- Standard margin applies

**Note**: For US brokers (tastytrade, webull), CNC is the standard product type for all position types.

## Validity Types

Most brokers support:

| Validity | Meaning |
|----------|---------|
| DAY | Valid for today only |
| IOC | Immediate or Cancel (execute now or cancel) |
| GTC | Good Till Cancelled (until manually cancelled) |

**Note**: OpenAlgo typically uses DAY validity.

## Common Order Mistakes

### Mistake 1: SL Order Triggered Immediately

**Problem**: SL buy at trigger $150 when price is $148
**Why**: Trigger price is below current price (already triggered!)
**Fix**: For SL BUY, trigger must be ABOVE current price

### Mistake 2: Limit Order Not Executing

**Problem**: BUY LIMIT at $140 when price is $150
**Why**: Price never reached your limit
**Fix**: Set realistic limit prices or use market orders

### Mistake 3: Wrong Product Type

**Problem**: Using wrong product type for US broker
**Why**: US brokers use CNC for all position types
**Fix**: Use CNC for overnight/delivery positions with US brokers

## Quick Decision Guide

```
Need immediate execution?
├── YES → MARKET
└── NO → Want specific price?
         ├── YES → LIMIT
         └── NO → Setting stop-loss?
                  ├── YES → Need guaranteed execution?
                  │         ├── YES → SL-M
                  │         └── NO → SL
                  └── NO → Reconsider requirements
```

---

**Previous**: [10 - Placing Your First Order](../10-placing-first-order/README.md)

**Next**: [12 - Smart Orders](../12-smart-orders/README.md)
