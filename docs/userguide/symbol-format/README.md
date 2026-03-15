# OpenAlgo Symbol Format Guide

## Introduction

OpenAlgo uses a standardized symbol format across all exchanges and brokers. This uniform symbology eliminates the need for traders to adapt to varied broker-specific formats, streamlining algorithm development and execution.

Understanding the symbol format is **essential** for placing orders correctly. Incorrect symbol format is the most common cause of order failures.

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OpenAlgo Symbol Format                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  EQUITY                                                                      │
│  ───────                                                                     │
│  Format: [Symbol]                                                           │
│  Example: AAPL, TSLA, MSFT, AMZN                                            │
│                                                                              │
│  FUTURES                                                                     │
│  ────────                                                                    │
│  Format: /[Symbol]                                                          │
│  Example: /ES (E-mini S&P 500), /CL (Crude Oil), /GC (Gold)               │
│                                                                              │
│  OPTIONS                                                                     │
│  ────────                                                                    │
│  Format: [Symbol][YYMMDD][C/P][Strike×1000 zero-padded to 8 digits]        │
│  Example: AAPL250117C00200000 (AAPL Jan 17 2025 $200 Call)                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Equity Symbol Format

Equity symbols use the base trading symbol (ticker) without any modifications.

### Format

```
[Base Symbol]
```

### Examples

| Company | Ticker | OpenAlgo Symbol |
|---------|--------|-----------------|
| Apple Inc. | AAPL | `AAPL` |
| Tesla Inc. | TSLA | `TSLA` |
| Microsoft Corp. | MSFT | `MSFT` |
| Amazon.com Inc. | AMZN | `AMZN` |
| NVIDIA Corp. | NVDA | `NVDA` |
| Alphabet Inc. | GOOGL | `GOOGL` |
| Meta Platforms | META | `META` |

### Usage

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

## Futures Symbol Format

US futures symbols use a leading slash followed by the root symbol.

### Format

```
/[Root Symbol]
```

Where:
- **Root Symbol**: The futures root identifier (e.g., ES, CL, GC, NQ)

### Examples

| Description | OpenAlgo Symbol |
|-------------|-----------------|
| E-mini S&P 500 Future | `/ES` |
| E-mini Nasdaq-100 Future | `/NQ` |
| Crude Oil Future (WTI) | `/CL` |
| Gold Future | `/GC` |
| 10-Year Treasury Note Future | `/ZN` |
| Euro FX Future | `/6E` |

### Usage

```json
{
  "symbol": "/ES",
  "exchange": "FUTURES",
  "action": "BUY",
  "quantity": "1",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## Options Symbol Format

US equity options symbols follow the OCC (Options Clearing Corporation) standard format.

### Format

```
[Symbol][YYMMDD][C/P][Strike×1000 zero-padded to 8 digits]
```

Where:
- **Symbol**: Underlying ticker (right-padded to 6 chars for OCC, but OpenAlgo accepts compact form)
- **YYMMDD**: Two-digit year, month, day of expiry
- **C**: Call option
- **P**: Put option
- **Strike**: Strike price multiplied by 1000, zero-padded to 8 digits

### Examples

#### Equity Options

| Description | OpenAlgo Symbol |
|-------------|-----------------|
| AAPL $200 Call, Jan 17 2025 | `AAPL250117C00200000` |
| AAPL $190 Put, Jan 17 2025 | `AAPL250117P00190000` |
| TSLA $250 Call, Feb 21 2025 | `TSLA250221C00250000` |
| MSFT $420 Put, Mar 21 2025 | `MSFT250321P00420000` |
| NVDA $130 Call, Apr 17 2025 | `NVDA250417C00130000` |

#### Index Options

| Description | OpenAlgo Symbol |
|-------------|-----------------|
| SPY $500 Call, Jan 17 2025 | `SPY250117C00500000` |
| QQQ $450 Put, Jan 17 2025 | `QQQ250117P00450000` |

### Usage

```json
{
  "symbol": "AAPL250117C00200000",
  "exchange": "OPTIONS",
  "action": "BUY",
  "quantity": "1",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## Exchange Codes

OpenAlgo uses standardized exchange codes to identify trading venues.

### US Market Exchanges

| Exchange | Code | Description |
|----------|------|-------------|
| US Equity | `EQUITY` | Stocks and ETFs (AAPL, TSLA, SPY) |
| US Options | `OPTIONS` | Equity and index options |
| US Futures | `FUTURES` | Index, commodity, and rate futures (/ES, /CL) |
| US Futures Options | `FUTURES_OPTION` | Options on futures contracts |

## Common US Index ETF Symbols

### Broad Market ETFs (Exchange: EQUITY)

| Symbol | Description |
|--------|-------------|
| `SPY` | SPDR S&P 500 ETF |
| `QQQ` | Invesco Nasdaq-100 ETF |
| `IWM` | iShares Russell 2000 ETF |
| `DIA` | SPDR Dow Jones Industrial Average ETF |
| `VTI` | Vanguard Total Stock Market ETF |

### Common Futures (Exchange: FUTURES)

| Symbol | Description |
|--------|-------------|
| `/ES` | E-mini S&P 500 |
| `/NQ` | E-mini Nasdaq-100 |
| `/RTY` | E-mini Russell 2000 |
| `/CL` | Crude Oil (WTI) |
| `/GC` | Gold |
| `/ZN` | 10-Year Treasury Note |

## Product Types

| Product | Description | Use Case |
|---------|-------------|----------|
| `CNC` | Cash and Carry | All US trading (equity, options, futures) |

## Complete Order Examples

### Equity Market Order

```json
{
  "apikey": "your-api-key",
  "strategy": "MyStrategy",
  "symbol": "AAPL",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "100",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Equity Limit Order

```json
{
  "apikey": "your-api-key",
  "strategy": "Investment",
  "symbol": "TSLA",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "10",
  "pricetype": "LIMIT",
  "price": "245.00",
  "product": "CNC"
}
```

### Futures Order

```json
{
  "apikey": "your-api-key",
  "strategy": "FuturesStrategy",
  "symbol": "/ES",
  "exchange": "FUTURES",
  "action": "BUY",
  "quantity": "1",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Options Order

```json
{
  "apikey": "your-api-key",
  "strategy": "OptionsStrategy",
  "symbol": "AAPL250117C00200000",
  "exchange": "OPTIONS",
  "action": "BUY",
  "quantity": "1",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Crude Oil Futures Order

```json
{
  "apikey": "your-api-key",
  "strategy": "CommodityStrategy",
  "symbol": "/CL",
  "exchange": "FUTURES",
  "action": "BUY",
  "quantity": "1",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## Multi-Leg Options Strategies

### Bull Call Spread

```json
{
  "apikey": "your-api-key",
  "strategy": "BullCallSpread",
  "orders": [
    {
      "symbol": "AAPL250117C00190000",
      "exchange": "OPTIONS",
      "action": "BUY",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "AAPL250117C00200000",
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
  "apikey": "your-api-key",
  "strategy": "IronCondor",
  "orders": [
    {
      "symbol": "SPY250117C00510000",
      "exchange": "OPTIONS",
      "action": "SELL",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "SPY250117C00520000",
      "exchange": "OPTIONS",
      "action": "BUY",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "SPY250117P00480000",
      "exchange": "OPTIONS",
      "action": "SELL",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    },
    {
      "symbol": "SPY250117P00470000",
      "exchange": "OPTIONS",
      "action": "BUY",
      "quantity": "1",
      "pricetype": "MARKET",
      "product": "CNC"
    }
  ]
}
```

## Finding the Correct Symbol

### Method 1: OpenAlgo Symbol Search

1. Go to OpenAlgo dashboard
2. Navigate to **Search** page
3. Enter the symbol name
4. Copy the exact symbol from results

### Method 2: Master Contract Database

OpenAlgo maintains a master contract database that maps broker symbols to standardized symbols. The database is updated daily.

### Method 3: API Endpoint

```
POST /api/v1/search
{
  "apikey": "your-key",
  "query": "NIFTY"
}
```

## Common Mistakes

### Mistake 1: Wrong Options Date Format

```
❌ AAPL25JAN17C00200000     (wrong date order - must be YYMMDD)
❌ AAPL2025-01-17C00200000  (no dashes allowed)
✅ AAPL250117C00200000      (correct: YYMMDD)
```

### Mistake 2: Wrong Exchange Code

```
❌ symbol: "AAPL250117C00200000", exchange: "EQUITY"  (wrong exchange for options)
✅ symbol: "AAPL250117C00200000", exchange: "OPTIONS"  (correct)
```

### Mistake 3: Wrong Strike Encoding

```
❌ AAPL250117C200            (missing zero-padding)
✅ AAPL250117C00200000       (correct: strike $200 × 1000 = 200000, padded to 8 digits)
```

### Mistake 4: Case Sensitivity

```
❌ "aapl", "Aapl"  (lowercase/mixed case)
✅ "AAPL"          (uppercase - correct)
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Symbol not found | Incorrect format | Verify symbol using Search |
| Invalid exchange | Wrong exchange code | Match exchange to instrument type |
| Order rejected | Expired contract | Update to current expiry |
| Invalid product | Wrong product type | Use CNC for all US instruments |

## Symbol Format Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OpenAlgo Symbol Quick Reference                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TYPE          FORMAT                         EXAMPLE                       │
│  ────          ──────                         ───────                       │
│  Equity        [Symbol]                       AAPL                          │
│  Future        /[RootSymbol]                  /ES, /CL, /GC                 │
│  Call Option   [Symbol][YYMMDD]C[Strike8]     AAPL250117C00200000           │
│  Put Option    [Symbol][YYMMDD]P[Strike8]     AAPL250117P00190000           │
│                                                                              │
│  EXCHANGE CODES                                                             │
│  ──────────────                                                             │
│  EQUITY         = US equities and ETFs                                      │
│  OPTIONS        = US equity and index options                               │
│  FUTURES        = US futures (/ES, /CL, /GC)                               │
│  FUTURES_OPTION = Options on futures                                        │
│                                                                              │
│  PRODUCT CODES                                                              │
│  ─────────────                                                              │
│  CNC  = All US instruments (equity, options, futures)                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Return to**: [User Guide Home](../README.md)
