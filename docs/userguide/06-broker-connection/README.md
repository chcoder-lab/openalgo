# 06 - Broker Connection

## Introduction

OpenAlgo supports Webull and tastytrade through a unified interface. This guide covers connecting your broker account and understanding the authentication process.

## Supported Brokers

### Full List of Supported Brokers

| Broker | Auth Type | Auto Login |
|--------|-----------|------------|
| Webull | OAuth2 | No |
| tastytrade | OAuth2 | No |

## Getting Broker API Credentials

### Webull

See [webullapidocs.md](webullapidocs.md) for full credential setup instructions.

**Summary**:
- Requires two sets of credentials: OAuth2 (trading) and App Key (market data)
- Apply for API access via Webull's developer program
- Sandbox environment available for testing

### tastytrade

See [tastytradeapidocs.md](tastytradeapidocs.md) for full credential setup instructions.

**Summary**:
- OAuth2 authorization code flow
- Requires a tastytrade developer account
- Certification (sandbox) environment available for testing

## Configuring Broker in OpenAlgo

### Configure via Web Interface

1. Login to OpenAlgo
2. Go to **Profile** → **Broker Configuration**
3. Select your broker from dropdown
4. Enter credentials in the form
5. Click **Save**

## Logging into Your Broker

### OAuth2 Brokers (Webull, tastytrade)

1. In OpenAlgo, click **Login to Broker**
2. You're redirected to the broker's login page
3. Enter your broker credentials
4. Approve the connection
5. Automatically redirected back to OpenAlgo

```
OpenAlgo → Broker Login Page → Enter Credentials → Approve → Back to OpenAlgo
```

## Understanding Authentication

### Daily Login Requirement

Most brokers require you to login every trading day:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Typical Trading Day (US ET)                   │
│                                                                  │
│  8:00 AM  - Login to OpenAlgo                                   │
│  8:30 AM  - Login to Broker                                     │
│  9:30 AM  - Market Opens (you're ready to trade)                │
│  4:00 PM  - Market Closes                                       │
│  8:00 PM  - After-hours trading ends                            │
│                                                                  │
│  Next Day - Login again                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Token Storage

OpenAlgo stores broker tokens:
- Encrypted in database
- Never stored in plain text
- Auto-deleted on logout

## Connection Status

### Checking Connection

In OpenAlgo dashboard, you'll see:

| Status | Meaning |
|--------|---------|
| 🟢 Connected | Broker session active |
| 🔴 Disconnected | Need to login |
| 🟡 Connecting | Login in progress |

### What "Connected" Means

When connected, you can:
- Place orders
- View positions
- Check holdings
- Get market data

### What Happens When Disconnected

- Orders will fail
- Real-time data stops
- Need to re-login

## Handling Multiple Brokers

### Switching Brokers

1. Select the new broker in **Profile** → **Broker Configuration**
2. Update corresponding credentials and redirect URL
3. Save and login to the new broker

**Note**: Only one broker active at a time per user session

### Running Multiple Instances

To use multiple brokers simultaneously:

1. Install OpenAlgo in separate folders
2. Configure each with different broker
3. Run on different ports

```bash
# Instance 1 (Webull on port 5001)
FLASK_PORT=5001 uv run app.py

# Instance 2 (tastytrade on port 5002)
FLASK_PORT=5002 uv run app.py
```

## Connection Troubleshooting

### Issue: "Invalid API credentials"

**Causes**:
- Typo in API key/secret
- Extra spaces in credentials
- Expired credentials

**Solutions**:
- Double-check credentials
- Remove any spaces
- Regenerate from broker

### Issue: "Broker not responding"

**Causes**:
- Broker server down
- Network issues
- Market closed

**Solutions**:
- Check broker status page
- Try broker's website
- Wait and retry

### Issue: "Session expired"

**Normal behavior** - sessions expire daily.

**Solution**: Login again before the market opens.

## Best Practices

### Security

1. **Never share** broker credentials
2. **Use strong passwords** for broker accounts
3. **Enable 2FA** on broker account
4. **Restrict IP** if broker supports it

### Reliability

1. **Login early** - Before market opens (8:00-9:00 AM ET)
2. **Check status** - Verify connection before trading
3. **Have backup** - Know broker's web/mobile app as fallback
4. **Monitor** - Watch for disconnections

### For VPS Users

1. Use static IP if possible
2. Some brokers restrict new IPs — whitelist your VPS IP
3. Consider VPN if required

## Broker-Specific Notes

### Webull
- Two credential sets required: OAuth2 (trading) + App Key (market data)
- Supports sandbox environment for testing (`BROKER_API_ENV=sandbox`)
- Request API access through Webull's developer program

### tastytrade
- OAuth2 only — no separate market data credentials needed
- Certification environment available (`TASTYTRADE_ENV=sandbox`)
- Streamer WebSocket available for real-time market data

---

**Previous**: [05 - First-Time Setup](../05-first-time-setup/README.md)

**Next**: [07 - Dashboard Overview](../07-dashboard-overview/README.md)
