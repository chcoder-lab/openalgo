# 16 - TradingView Integration

## Introduction

TradingView is a popular charting platform with powerful Pine Script strategy capabilities. OpenAlgo connects TradingView alerts to your broker for automated order execution.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TradingView → OpenAlgo Flow                              │
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────┐  │
│  │ TradingView │     │   Webhook   │     │  OpenAlgo   │     │  Broker  │  │
│  │   Alert     │────▶│   Request   │────▶│   Server    │────▶│   API    │  │
│  │  Triggers   │     │             │     │             │     │          │  │
│  └─────────────┘     └─────────────┘     └─────────────┘     └──────────┘  │
│                                                                              │
│  Pine Script        JSON Payload        Validates &         Executes       │
│  condition met      sent to URL         processes           trade          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. TradingView account (free or paid)
2. OpenAlgo running and accessible via internet
3. API key generated in OpenAlgo
4. Broker connected and logged in

## Making OpenAlgo Accessible for Webhooks

TradingView webhooks need to reach your OpenAlgo server from the internet.

### Recommended: Production Server with Domain

Deploy OpenAlgo on an Ubuntu server using `install.sh` (see [Installation Guide](../04-installation/README.md)):

```
Webhook URL: https://yourdomain.com/api/v1/placeorder
```

This is the **recommended approach** for live trading because:
- Your domain provides a permanent, stable URL
- SSL/TLS is auto-configured with Let's Encrypt
- Security headers are properly set
- Full server uptime under your control

### Alternative: Webhook Tunneling Services

If you don't have a domain or are testing locally, use a tunnel service **for webhooks only**:

| Service | Command | URL Format |
|---------|---------|------------|
| **ngrok** | `ngrok http 5000` | `https://abc123.ngrok.io` |
| **devtunnel** (Microsoft) | `devtunnel host -p 5000` | `https://xxxxx.devtunnels.ms` |
| **Cloudflare Tunnel** | `cloudflared tunnel --url http://localhost:5000` | `https://xxxxx.trycloudflare.com` |

**ngrok:**
```bash
# Install from ngrok.com
ngrok http 5000
# Copy the https URL provided
```

**devtunnel (Microsoft):**
```bash
# Install: https://aka.ms/devtunnels
devtunnel user login
devtunnel host -p 5000
# Copy the https URL provided
```

**Cloudflare Tunnel:**
```bash
# Install cloudflared
cloudflared tunnel --url http://localhost:5000
# Copy the https URL provided
```

**Important**: Tunnel services are **only for webhooks**, not for running the full application. Always run OpenAlgo on your own server for production use.

| Aspect | Domain (Recommended) | Tunnel Services |
|--------|---------------------|-----------------|
| URL stability | Permanent | Changes on restart |
| SSL certificate | Let's Encrypt (your control) | Provider-managed |
| Uptime | Your server uptime | Depends on tunnel service |
| Rate limits | Your control | Provider's limits |
| Security headers | Fully configured | Basic |

## Setting Up TradingView Alerts

### Step 1: Create Your Strategy

In TradingView Pine Script:

```pine
//@version=5
strategy("My OpenAlgo Strategy", overlay=true)

// Simple moving average crossover
fastMA = ta.sma(close, 9)
slowMA = ta.sma(close, 21)

// Entry conditions
longCondition = ta.crossover(fastMA, slowMA)
shortCondition = ta.crossunder(fastMA, slowMA)

// Execute trades
if (longCondition)
    strategy.entry("Long", strategy.long)

if (shortCondition)
    strategy.entry("Short", strategy.short)
```

### Step 2: Create Alert

1. Right-click on chart or press `Alt+A`
2. Select **Create Alert**
3. Configure:
   - **Condition**: Your strategy name
   - **Alert actions**: Check "Webhook URL"

### Step 3: Configure Webhook URL

```
https://your-openalgo-url/api/v1/placesmartorder
```

Or for regular orders:
```
https://your-openalgo-url/api/v1/placeorder
```

### Step 4: Configure Alert Message

Use this JSON template in the **Message** field:

```json
{
  "apikey": "YOUR_API_KEY",
  "strategy": "{{strategy.order.id}}",
  "symbol": "{{ticker}}",
  "exchange": "EQUITY",
  "action": "{{strategy.order.action}}",
  "quantity": "{{strategy.order.contracts}}",
  "position_size": "{{strategy.position_size}}",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## TradingView Variables

### Strategy Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{strategy.order.action}}` | BUY or SELL | BUY |
| `{{strategy.order.contracts}}` | Order quantity | 100 |
| `{{strategy.position_size}}` | Current position | 100 or -100 |
| `{{strategy.order.id}}` | Order/Strategy ID | Long |
| `{{strategy.order.price}}` | Order price | 625.50 |

### Ticker Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ticker}}` | Symbol name | AAPL |
| `{{exchange}}` | Exchange name | EQUITY |
| `{{close}}` | Current close price | 625.50 |
| `{{time}}` | Alert time | 2024-01-25... |

## Alert Message Templates

### Basic Order (Market)

```json
{
  "apikey": "YOUR_API_KEY",
  "strategy": "TVStrategy",
  "symbol": "{{ticker}}",
  "exchange": "EQUITY",
  "action": "{{strategy.order.action}}",
  "quantity": "100",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Smart Order (Position-Aware)

```json
{
  "apikey": "YOUR_API_KEY",
  "strategy": "TVSmart",
  "symbol": "{{ticker}}",
  "exchange": "EQUITY",
  "action": "{{strategy.order.action}}",
  "quantity": "{{strategy.order.contracts}}",
  "position_size": "{{strategy.position_size}}",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Limit Order

```json
{
  "apikey": "YOUR_API_KEY",
  "strategy": "TVLimit",
  "symbol": "{{ticker}}",
  "exchange": "EQUITY",
  "action": "{{strategy.order.action}}",
  "quantity": "100",
  "pricetype": "LIMIT",
  "price": "{{strategy.order.price}}",
  "product": "CNC"
}
```

### Options Order

```json
{
  "apikey": "YOUR_API_KEY",
  "strategy": "TVOptions",
  "symbol": "AAPL250117C00200000",
  "exchange": "OPTIONS",
  "action": "{{strategy.order.action}}",
  "quantity": "1",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## Symbol Mapping

### Equity Symbols

TradingView symbols map directly:

| TradingView | OpenAlgo |
|-------------|----------|
| AAPL | AAPL |
| TSLA | TSLA |
| MSFT | MSFT |

### Index Symbols

| TradingView | OpenAlgo Exchange |
|-------------|-------------------|
| SPX | EQUITY (use INDEX product) |
| NDX | EQUITY (use INDEX product) |

### Options Symbols

For options, you need to construct the symbol manually using OCC format:

```
Format: SYMBOL + EXPIRY (YYMMDD) + CALL/PUT + STRIKE (8 digits, padded)

Examples:
- AAPL250117C00200000 (AAPL Jan 17 2025 $200 Call)
- TSLA250117P00250000 (TSLA Jan 17 2025 $250 Put)
- /ES250321 (E-mini S&P 500 March 2025 Future)
```

## Testing Your Setup

### Step 1: Enable Analyzer Mode

Before live trading, test in Analyzer Mode:

1. Go to **Analyzer** page in OpenAlgo
2. Enable **Analyzer Mode**
3. This routes orders to sandbox

### Step 2: Trigger Test Alert

In TradingView:
1. Create alert with your webhook
2. Set condition to trigger immediately (for testing)
3. Or manually trigger: Right-click alert → **Trigger**

### Step 3: Verify in OpenAlgo

Check:
1. **Order Book** - Order should appear
2. **Positions** - Position should be created
3. **Logs** - Check for any errors

## Common Pine Script Patterns

### Long Only Strategy

```pine
//@version=5
strategy("Long Only", overlay=true)

longCondition = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))
exitCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))

if (longCondition)
    strategy.entry("Long", strategy.long)

if (exitCondition)
    strategy.close("Long")
```

Alert message for entry:
```json
{
  "apikey": "KEY",
  "strategy": "LongOnly",
  "symbol": "{{ticker}}",
  "exchange": "EQUITY",
  "action": "BUY",
  "quantity": "100",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

### Reversal Strategy

```pine
//@version=5
strategy("Reversal", overlay=true)

longCondition = ta.crossover(ta.rsi(close, 14), 30)
shortCondition = ta.crossunder(ta.rsi(close, 14), 70)

if (longCondition)
    strategy.entry("Long", strategy.long)

if (shortCondition)
    strategy.entry("Short", strategy.short)
```

Use smart order for automatic reversal:
```json
{
  "apikey": "KEY",
  "strategy": "Reversal",
  "symbol": "{{ticker}}",
  "exchange": "EQUITY",
  "action": "{{strategy.order.action}}",
  "quantity": "100",
  "position_size": "{{strategy.position_size}}",
  "pricetype": "MARKET",
  "product": "CNC"
}
```

## Troubleshooting

### Alert Not Triggering

| Issue | Solution |
|-------|----------|
| Strategy not loaded | Add strategy to chart |
| Alert expired | Check alert expiration date |
| Webhook not enabled | Verify webhook checkbox |

### Order Not Executing

| Issue | Solution |
|-------|----------|
| Invalid API key | Check API key in message |
| Broker not logged in | Login to broker |
| Market closed | Wait for market hours |
| Invalid symbol | Check symbol mapping |

### Checking Logs

1. Go to **Traffic Logs** in OpenAlgo
2. Filter by "webhook"
3. Check request body and response

### Common Errors

```
"error": "Invalid API key"
→ Generate new API key and update alert

"error": "Symbol not found"
→ Check symbol exists in master contract

"error": "Insufficient margin"
→ Add funds or reduce quantity
```

## Best Practices

### 1. Test Thoroughly

- Always test in Analyzer Mode first
- Use small quantities initially
- Monitor first few live trades

### 2. Use Smart Orders

- Better for reversal strategies
- Handles position management automatically
- Prevents duplicate positions

### 3. Handle Multiple Symbols

Create separate alerts for each symbol or use dynamic symbols:

```json
{
  "symbol": "{{ticker}}",
  ...
}
```

### 4. Set Alert Expiration

- Don't use "Once" for live strategies
- Use appropriate expiration
- Premium plans have longer expiration

### 5. Monitor Execution

- Keep OpenAlgo dashboard open
- Check order book regularly
- Set up Telegram notifications

## Alert Frequency Limits

| TradingView Plan | Alert Limit |
|------------------|-------------|
| Free | 1 alert |
| Essential | 20 alerts |
| Plus | 100 alerts |
| Premium | 400 alerts |
| Expert | 800 alerts |

---

**Previous**: [15 - Analyzer Mode (Sandbox Testing)](../15-analyzer-mode/README.md)

**Next**: [17 - Amibroker Integration](../17-amibroker-integration/README.md)
