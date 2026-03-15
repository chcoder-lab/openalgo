# 13 - Basket Orders

## Introduction

Basket Orders allow you to place multiple orders simultaneously with a single API call. This is essential for strategies that require executing trades across multiple symbols at once.

## What is a Basket Order?

A basket order bundles multiple individual orders into one request:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Basket Order Structure                                │
│                                                                              │
│  Single API Request                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Order 1: BUY 100 AAPL                                              │   │
│  │  Order 2: BUY 50 TSLA                                               │   │
│  │  Order 3: SELL 25 MSFT                                              │   │
│  │  Order 4: BUY 200 NVDA                                              │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                               │
│                              ▼                                               │
│                    All orders sent to broker                                │
│                              │                                               │
│                              ▼                                               │
│                   Individual order responses                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Use Cases

### 1. Index Replication

Buy S&P 500 constituents proportionally:

```
Basket:
- BUY 100 AAPL
- BUY 50 MSFT
- BUY 75 AMZN
- BUY 200 TSLA
... (selected stocks)
```

### 2. Sector Rotation

Rotate into technology sector:

```
Basket:
- SELL 100 XOM (exit energy)
- SELL 50 JPM (exit financials)
- BUY 100 AAPL (enter tech)
- BUY 100 MSFT (enter tech)
```

### 3. Pair Trading

Long-short pair execution:

```
Basket:
- BUY 100 AAPL (long)
- SELL 100 MSFT (short)
```

### 4. Options Strategies

Multi-leg option strategies:

```
Iron Condor Basket:
- SELL 1 AAPL250117C00200000
- BUY 1 AAPL250117C00210000
- SELL 1 AAPL250117P00180000
- BUY 1 AAPL250117P00170000
```

## Basket Order API

### Endpoint

```
POST /api/v1/basketorder
```

### Request Format

```json
{
  "apikey": "your-api-key",
  "strategy": "BasketStrategy",
  "orders": [
    {
      "symbol": "AAPL",
      "exchange": "EQUITY",
      "action": "BUY",
      "quantity": "100",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "TSLA",
      "exchange": "EQUITY",
      "action": "BUY",
      "quantity": "50",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "MSFT",
      "exchange": "EQUITY",
      "action": "SELL",
      "quantity": "25",
      "pricetype": "MARKET",
      "product": "CNC"
    }
  ]
}
```

### Response

```json
{
  "status": "success",
  "results": [
    {
      "symbol": "AAPL",
      "status": "success",
      "orderid": "230125000012345"
    },
    {
      "symbol": "TSLA",
      "status": "success",
      "orderid": "230125000012346"
    },
    {
      "symbol": "MSFT",
      "status": "success",
      "orderid": "230125000012347"
    }
  ],
  "total_orders": 3,
  "successful": 3,
  "failed": 0
}
```

## Python Example

```python
from openalgo import api

client = api(api_key="your-key", host="http://127.0.0.1:5001")

# Define basket
basket = [
    {
        "symbol": "AAPL",
        "exchange": "EQUITY",
        "action": "BUY",
        "quantity": 100,
        "pricetype": "MARKET",
        "product": "CNC"
    },
    {
        "symbol": "TSLA",
        "exchange": "EQUITY",
        "action": "BUY",
        "quantity": 50,
        "pricetype": "MARKET",
        "product": "CNC"
    },
    {
        "symbol": "MSFT",
        "exchange": "EQUITY",
        "action": "BUY",
        "quantity": 25,
        "pricetype": "MARKET",
        "product": "CNC"
    }
]

# Place basket order
response = client.place_basket_order(
    orders=basket,
    strategy="PortfolioRebalance"
)

# Check results
for result in response['results']:
    print(f"{result['symbol']}: {result['status']}")
```

## Order Types in Baskets

### Market Orders (Recommended)

```json
{
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "100",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Limit Orders

```json
{
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "100",
  "pricetype": "LIMIT",
  "price": "190.00",
  "product": "CNC"
}
```

### Mixed Order Types

You can mix order types in a basket:

```json
{
  "orders": [
    {
      "symbol": "AAPL",
      "pricetype": "MARKET",
      ...
    },
    {
      "symbol": "TSLA",
      "pricetype": "LIMIT",
      "price": "250.00",
      ...
    }
  ]
}
```

## Basket Execution Behavior

### Parallel Execution

Orders are sent to broker in parallel:

```
Time 0ms:  All orders submitted
Time 50ms: AAPL executed
Time 55ms: TSLA executed
Time 60ms: MSFT executed
```

### Partial Success

Some orders may succeed while others fail:

```json
{
  "results": [
    {"symbol": "AAPL", "status": "success", "orderid": "123"},
    {"symbol": "TSLA", "status": "error", "message": "Insufficient margin"},
    {"symbol": "MSFT", "status": "success", "orderid": "124"}
  ],
  "successful": 2,
  "failed": 1
}
```

### No Atomicity

Important: Basket orders are NOT atomic!
- Each order is independent
- One failure doesn't cancel others
- You must handle partial fills

## Handling Partial Failures

```python
response = client.place_basket_order(orders=basket, strategy="MyStrategy")

# Check for failures
failed_orders = [r for r in response['results'] if r['status'] == 'error']

if failed_orders:
    print("Failed orders:")
    for order in failed_orders:
        print(f"  {order['symbol']}: {order['message']}")

    # Retry or handle as needed
    # ...
```

## Limits and Best Practices

### Order Limits

| Limit Type | Typical Value |
|------------|---------------|
| Max orders per basket | 50 |
| Max orders per second | 10 |
| Max daily orders | Broker dependent |

### Best Practices

1. **Keep baskets manageable**: 10-20 orders ideal
2. **Use market orders** for guaranteed execution
3. **Handle partial failures** in your code
4. **Test in Analyzer mode** first
5. **Monitor execution** in order book

### Error Handling Example

```python
def execute_basket_with_retry(basket, max_retries=3):
    response = client.place_basket_order(orders=basket, strategy="MyStrategy")

    failed = [r for r in response['results'] if r['status'] == 'error']

    retries = 0
    while failed and retries < max_retries:
        # Extract failed orders
        failed_symbols = [f['symbol'] for f in failed]
        retry_basket = [o for o in basket if o['symbol'] in failed_symbols]

        # Wait and retry
        time.sleep(1)
        response = client.place_basket_order(orders=retry_basket, strategy="MyStrategy")

        failed = [r for r in response['results'] if r['status'] == 'error']
        retries += 1

    return response
```

## Options Strategy Baskets

### Bull Call Spread

```json
{
  "apikey": "your-key",
  "strategy": "BullCallSpread",
  "orders": [
    {
      "symbol": "AAPL250117C00200000",
      "exchange": "OPTIONS",
      "action": "BUY",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "AAPL250117C00210000",
      "exchange": "OPTIONS",
      "action": "SELL",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    }
  ]
}
```

### Iron Condor

```json
{
  "strategy": "IronCondor",
  "orders": [
    {"symbol": "AAPL250117C00200000", "action": "SELL", ...},
    {"symbol": "AAPL250117C00210000", "action": "BUY", ...},
    {"symbol": "AAPL250117P00180000", "action": "SELL", ...},
    {"symbol": "AAPL250117P00170000", "action": "BUY", ...}
  ]
}
```

## Basket vs Individual Orders

| Aspect | Basket | Individual |
|--------|--------|------------|
| API calls | 1 | Multiple |
| Speed | Faster | Slower |
| Complexity | Higher | Lower |
| Error handling | Complex | Simple |
| Best for | Multi-symbol strategies | Single symbol |

---

**Previous**: [12 - Smart Orders](../12-smart-orders/README.md)

**Next**: [14 - Positions & Holdings](../14-positions-holdings/README.md)
