# 02 - Key Concepts

## Introduction

Before diving into OpenAlgo, let's understand the key terms and concepts you'll encounter. This foundation will make everything else easier to understand.

## Core Concepts

### 1. API (Application Programming Interface)

**Simple Explanation**: An API is like a waiter in a restaurant. You (the customer) tell the waiter what you want, the waiter goes to the kitchen (the system), and brings back your food (the response).

**In OpenAlgo**: When TradingView wants to place an order, it sends a request to OpenAlgo's API. OpenAlgo processes it and sends the order to your broker.

```
TradingView → "Place BUY order for AAPL" → OpenAlgo API → Broker
```

### 2. API Key

**Simple Explanation**: Your API key is like a password that identifies you. It proves to OpenAlgo that the request is coming from an authorized source.

**Example**:
```
API Key: a1b2c3d4e5f6g7h8i9j0
```

**Important**:
- Keep your API key secret
- Never share it publicly
- Regenerate if compromised

### 3. Webhook

**Simple Explanation**: A webhook is like a doorbell. When something happens (like a TradingView alert), it "rings" your OpenAlgo server to notify it.

**How it works**:
```
TradingView Alert Triggers
        ↓
Webhook sends data to your URL
        ↓
OpenAlgo receives and processes
        ↓
Order placed with broker
```

**Your Webhook URL format**:
```
http://your-server:5000/api/v1/placeorder
```

### 4. Broker Token / Access Token

**Simple Explanation**: When you log into your broker through OpenAlgo, you get a temporary pass (token) that lets OpenAlgo place orders on your behalf.

**Characteristics**:
- Valid for one trading day
- Expires at end of day
- Must re-login daily (for most brokers)

### 5. Symbol Format

**Simple Explanation**: Every stock has a specific way to write its name that OpenAlgo understands.

**Examples**:
| What you want | OpenAlgo Symbol |
|---------------|-----------------|
| Apple Inc. equity | AAPL |
| Tesla equity | TSLA |
| Microsoft equity | MSFT |
| E-mini S&P 500 Future | /ES |
| Crude Oil Future | /CL |

### 6. Exchange Codes

**Simple Explanation**: Different markets have different codes.

| Exchange | Code | What it trades |
|----------|------|----------------|
| US Equity Market | EQUITY | Stocks (AAPL, TSLA, MSFT) |
| US Options Market | OPTIONS | Equity options |
| US Futures Market | FUTURES | Index & commodity futures (/ES, /CL) |
| US Futures Options | FUTURES_OPTION | Options on futures |

## Order Concepts

### 7. Order Types

**Market Order**: Buy/sell immediately at current price
- Pros: Guaranteed execution
- Cons: Price may vary

**Limit Order**: Buy/sell only at your specified price or better
- Pros: Price control
- Cons: May not execute

**Stop-Loss (SL)**: Triggers when price reaches a level
- Used to limit losses

**Stop-Loss Market (SL-M)**: Stop-loss with market execution
- Triggers at stop price, executes at market

```
Example: AAPL at $175

Market Order: "Buy at whatever current price is"
Limit Order: "Buy only if price is $170 or less"
SL Order: "Sell if price drops to $160"
```

### 8. Product Types

**CNC (Cash and Carry)**: For standard equity and overnight positions
- Hold stocks overnight/long-term
- No intraday leverage
- Standard US brokerage account behavior

```
Planning to hold for weeks? → Use CNC
Day trading equities? → Use CNC
Futures or options? → Use CNC
```

### 9. Action Types

| Action | Meaning |
|--------|---------|
| BUY | Purchase shares |
| SELL | Sell shares you own |
| SHORT | Sell shares you don't own (borrow and sell) |
| COVER | Buy back shorted shares |

## OpenAlgo Specific Concepts

### 10. Analyzer Mode (Sandbox Testing)

**Simple Explanation**: A practice mode where you trade with sandbox capital ($100,000) but real market prices.

**Use it to**:
- Test strategies without risk
- Learn the platform
- Validate before going live

```
Analyzer Mode ON  → Orders go to sandbox account
Analyzer Mode OFF → Orders go to real broker
```

### 11. Action Center

**Simple Explanation**: A holding area where orders wait for your approval before being sent to the broker.

**Two Modes**:
- **Auto Mode**: Orders execute immediately
- **Semi-Auto Mode**: Orders wait in Action Center for approval

**Use Semi-Auto when**:
- You want to review before execution
- Managing client accounts
- Regulatory compliance required

### 12. Strategy Name

**Simple Explanation**: A label you give to identify which trading system generated an order.

**Example**:
```
Strategy: "MA_Crossover"
Strategy: "RSI_Oversold"
Strategy: "Breakout_System"
```

**Why it matters**:
- Track P&L by strategy
- Filter orders by strategy
- Debug which system placed what

### 13. Smart Order

**Simple Explanation**: An intelligent order that considers your current position before deciding what to do.

**Example**:
```
You have: 100 shares of AAPL (LONG)
Smart Order says: "Go SHORT 100 shares"
What happens: Sells 200 shares (100 to close long + 100 to go short)
```

### 14. Split Order

**Simple Explanation**: Breaking a large order into smaller pieces to avoid market impact.

**Example**:
```
You want: Buy 10,000 shares
Split into: 10 orders of 1,000 shares each
```

## Flow Concepts

### 15. Flow (Visual Strategy Builder)

**Simple Explanation**: A drag-and-drop tool to create trading logic without coding.

**Components**:
- **Nodes**: Building blocks (conditions, actions)
- **Edges**: Connections between nodes
- **Triggers**: What starts the flow

```
[Webhook Trigger] → [Check Condition] → [Place Order] → [Send Telegram]
```

## Authentication Concepts

### 16. Two-Factor Authentication (TOTP)

**Simple Explanation**: An extra security layer using a 6-digit code from an app like Google Authenticator.

**Flow**:
```
Enter password → Enter 6-digit code → Access granted
```

### 17. Session

**Simple Explanation**: The period you're logged into OpenAlgo. Sessions expire for security.

**Browser Session**: Your OpenAlgo web login
**Broker Session**: Your broker connection (usually daily)

## Data Concepts

### 18. LTP (Last Traded Price)

**Simple Explanation**: The most recent price at which a stock was traded.

### 19. OHLC

**Simple Explanation**: Open, High, Low, Close - the four key prices for a time period.

```
Day's OHLC for AAPL:
Open: $172.00 (first trade)
High: $178.50 (highest)
Low: $171.00 (lowest)
Close: $176.25 (last trade)
```

### 20. Market Depth

**Simple Explanation**: Shows pending buy and sell orders at different price levels.

```
        BUY                 SELL
Qty    Price    |    Price    Qty
500    $174.95  |    $175.05  800
1000   $174.90  |    $175.10  1200
750    $174.85  |    $175.15  500
```

## Quick Reference Card

| Term | One-Line Definition |
|------|---------------------|
| API | Communication interface between systems |
| API Key | Your secret password for API access |
| Webhook | URL that receives external notifications |
| Token | Temporary broker access pass |
| Symbol | Stock identifier (e.g., AAPL) |
| Exchange | Market where stock trades (EQUITY, OPTIONS, etc.) |
| Market Order | Execute immediately at any price |
| Limit Order | Execute only at specified price |
| CNC | Standard trading (equity, overnight, and derivatives) |
| Analyzer | Sandbox testing mode |
| Action Center | Order approval queue |
| Smart Order | Position-aware order |
| Flow | Visual strategy builder |
| LTP | Latest stock price |

---

**Previous**: [02 - Why Build with OpenAlgo](../02-why-build-with-openalgo/README.md)

**Next**: [03 - System Requirements](../03-system-requirements/README.md)
