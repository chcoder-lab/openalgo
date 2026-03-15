# 06 - Broker Connection — Webull

## OpenAlgo Setup

Webull uses two separate credential sets in OpenAlgo:

| OpenAlgo Field | Webull Credential | Purpose |
|----------------|-------------------|---------|
| `BROKER_API_KEY` | Client ID | OAuth2 trading access |
| `BROKER_API_SECRET` | Client Secret | OAuth2 trading access |
| `BROKER_API_KEY_MARKET` | App Key | Market data token (HMAC-SHA1 signed) |
| `BROKER_API_SECRET_MARKET` | App Secret | Market data token (HMAC-SHA1 signed) |

### Environment

Set `BROKER_API_ENV` in your `.env` to switch between environments:

| Value | Environment | Trade API | OAuth API |
|-------|-------------|-----------|-----------|
| `sandbox` (default) | UAT / Test | `http://us-openapi-alb.uat.webullbroker.com` | `https://us-oauth-open-api.uat.webullbroker.com` |
| `production` | Live | `https://api.webull.com` | `https://us-oauth-open-api.webull.com` |

### Redirect URL

Register the following redirect URL with Webull when creating your OAuth app:

```
http://127.0.0.1:5001/webull/callback
```

For cloud deployments, replace with your public domain:
```
https://your-domain.com/webull/callback
```

### `.env` Configuration

```
BROKER_API_KEY        = 'your_client_id'
BROKER_API_SECRET     = 'your_client_secret'
BROKER_API_KEY_MARKET = 'your_app_key'
BROKER_API_SECRET_MARKET = 'your_app_secret'
REDIRECT_URL          = 'http://127.0.0.1:5001/webull/callback'
BROKER_API_ENV        = 'production'
VALID_BROKERS         = 'webull'
```

### Login Flow

1. In OpenAlgo, click **Login to Broker**
2. You are redirected to `passport.webull.com` to authorize
3. After approval, Webull redirects back to `/webull/callback` with an authorization code
4. OpenAlgo exchanges the code for an access token via `POST /openapi/oauth2/token`
5. Market data tokens are created automatically using App Key / App Secret with HMAC-SHA1 signing

> **Note:** After creating a market data token, Webull may send an SMS to your registered number for 2FA verification. Approve it in the Webull mobile app before making market data requests.

---

# Webull OpenAPI Documentation

## Guides

### Getting Started
- [Welcome to Webull API](https://developer.webull.com/apis/docs.md): Platform overview covering trading APIs, market data services, OAuth integration, and tools for building trading applications and brokerage solutions.
- [About Webull](https://developer.webull.com/apis/docs/about.md): Company introduction and regulatory background.
- [About Webull OpenAPI](https://developer.webull.com/apis/docs/about-open-api.md): OpenAPI platform capabilities and features overview.
- [Trading API Getting Started](https://developer.webull.com/apis/docs/sdk.md): SDK installation, development tools, and example code for trading and market data integration.
- [Additional Resources](https://developer.webull.com/apis/docs/resources.md): Learning materials, blog updates, support channels, and regulatory disclosures.

### Authentication
- [Authentication Overview](https://developer.webull.com/apis/docs/authentication/overview.md): Digest signature authentication using App Key and App Secret with security best practices.
- [Individual Application Process](https://developer.webull.com/apis/docs/authentication/IndividualApplicationAPI.md): Step-by-step guide for individual users to apply for API access and generate API keys.
- [Institution Application Process](https://developer.webull.com/apis/docs/authentication/apply.md): Institutional API application process, authorization workflow, and API key creation.
- [Signature](https://developer.webull.com/apis/docs/authentication/signature.md): HMAC-SHA1 signature generation, request composition, and required headers for API authentication.
- [Token](https://developer.webull.com/apis/docs/authentication/token.md): Token lifecycle management including creation, 2FA verification, status checks, storage, and usage in API requests.

### Market Data API
- [Market Data API Overview](https://developer.webull.com/apis/docs/market-data-api/overview.md): HTTP-based historical and real-time data retrieval (tick, snapshot, quotes, bars) for stocks, futures, and crypto; MQTT streaming via WebSocket/TCP; Python SDK; rate limits and subscription requirements.
- [Market Data API Getting Started](https://developer.webull.com/apis/docs/market-data-api/getting-started.md): Quick start guide for SDK installation, API key setup, and requesting historical or real-time market data with code examples.
- [Data API](https://developer.webull.com/apis/docs/market-data-api/data-api.md): HTTP-based market data access covering supported markets and data types.
- [Data Streaming API](https://developer.webull.com/apis/docs/market-data-api/data-streaming-api.md): Real-time market data streaming via MQTT protocol implementation guide.
- [Subscribe Advanced Quotes](https://developer.webull.com/apis/docs/market-data-api/subscribe-quotes.md): Browser-based guide to purchase and activate advanced real-time market data subscriptions.
- [Market Data API FAQ](https://developer.webull.com/apis/docs/market-data-api/faq.md): Frequently asked questions about market data access and usage.

### Trading API
- [Trading API Overview](https://developer.webull.com/apis/docs/trade-api/overview.md): Core trading functionality and capabilities overview.
- [Trading API Getting Started](https://developer.webull.com/apis/docs/trade-api/getting-started.md): Quick start guide for trading API integration.
- [Trading API - Accounts](https://developer.webull.com/apis/docs/trade-api/account.md): Account management, balance queries, and account information retrieval.
- [Trading API - Assets](https://developer.webull.com/apis/docs/trade-api/asset.md): Asset and position management operations.
- [Trading API - Orders](https://developer.webull.com/apis/docs/trade-api/trade.md): Order placement, modification, cancellation, and status tracking for stocks and options.
- [Trading API - Futures](https://developer.webull.com/apis/docs/trade-api/futures.md): Futures trading operations and contract management.
- [Trading API - Crypto](https://developer.webull.com/apis/docs/trade-api/crypto.md): Cryptocurrency trading functionality and digital asset operations.
- [Trading API - Event Contract](https://developer.webull.com/apis/docs/trade-api/event-contract.md): Event-based contract trading and prediction market operations.
- [Trading API - FAQs](https://developer.webull.com/apis/docs/trade-api/faq.md): Common questions and troubleshooting for trading API.

### Connect API
- [About Connect API](https://developer.webull.com/apis/docs/connect-api/about-connect-api.md): Connect API introduction and use cases for third-party integrations.
- [OAuth Integration Guide](https://developer.webull.com/apis/docs/connect-api/authentication.md): OAuth 2.0 implementation for user authorization and token management.

### General
- [Webull OpenAPI FAQs](https://developer.webull.com/apis/docs/faq.md): General frequently asked questions about Webull OpenAPI platform.

## API Reference

### Authentication & Token Management
- [Create Token](https://developer.webull.com/apis/docs/reference/create-token.md): Generate authentication tokens for API access.
- [Check Token](https://developer.webull.com/apis/docs/reference/check-token.md): Verify token validity and status.

### Market Data - Stocks
- [Stock Tick](https://developer.webull.com/apis/docs/reference/tick.md): Real-time tick-by-tick trade data for stocks.
- [Stock Snapshot](https://developer.webull.com/apis/docs/reference/snapshot.md): Current market snapshot with latest prices and statistics.
- [Stock Quotes](https://developer.webull.com/apis/docs/reference/quotes.md): Real-time bid/ask quotes and market depth.
- [Stock Footprint](https://developer.webull.com/apis/docs/reference/footprint.md): Order flow and volume profile analysis data.
- [Stock Historical Bars](https://developer.webull.com/apis/docs/reference/historical-bars.md): Historical OHLCV candlestick data for multiple symbols.
- [Stock Historical Bars (Single Symbol)](https://developer.webull.com/apis/docs/reference/bars.md): Historical OHLCV candlestick data for a single symbol.

### Market Data - Futures
- [Futures Tick](https://developer.webull.com/apis/docs/reference/futures-tick.md): Real-time tick-by-tick trade data for futures contracts.
- [Futures Snapshot](https://developer.webull.com/apis/docs/reference/futures-snapshot.md): Current futures market snapshot with latest prices and open interest.
- [Futures Footprint](https://developer.webull.com/apis/docs/reference/futures-footprint.md): Futures order flow and volume profile analysis.
- [Futures Depth of Book](https://developer.webull.com/apis/docs/reference/futures-depth-of-book.md): Market depth data for futures contracts.
- [Futures Historical Bars](https://developer.webull.com/apis/docs/reference/futures-historical-bars.md): Historical OHLCV data for futures contracts.

### Market Data - Crypto
- [Crypto Snapshot](https://developer.webull.com/apis/docs/reference/crypto-snapshot.md): Current cryptocurrency market snapshot with latest prices.
- [Crypto Candlesticks](https://developer.webull.com/apis/docs/reference/crypto-bars.md): Historical OHLCV candlestick data for cryptocurrencies.

### Market Data - Streaming
- [Subscribe Events](https://developer.webull.com/apis/docs/reference/subscribe.md): Subscribe to real-time market data streams via MQTT.
- [Unsubscribe Events](https://developer.webull.com/apis/docs/reference/unsubscribe.md): Unsubscribe from real-time market data streams.

### Instruments & Symbols
- [Stock Instruments](https://developer.webull.com/apis/docs/reference/instrument-list.md): List of available stock symbols and instrument details.
- [Crypto Instruments](https://developer.webull.com/apis/docs/reference/crypto-instrument-list.md): List of available cryptocurrency trading pairs.
- [Futures Products](https://developer.webull.com/apis/docs/reference/futures-products.md): Available futures product categories and specifications.
- [Futures Instrument by Code](https://developer.webull.com/apis/docs/reference/futures-instrument-list-by-code.md): Query futures contracts by product code.
- [Futures Instrument by Symbol](https://developer.webull.com/apis/docs/reference/futures-instrument-list.md): Query futures contracts by symbol.
- [Get Event Contract Series](https://developer.webull.com/apis/docs/reference/event-series-list.md): List available event contract series for prediction markets.
- [Get Event Contract Instrument](https://developer.webull.com/apis/docs/reference/event-market-list.md): Query specific event contract instruments and details.

### Account Management
- [Account List](https://developer.webull.com/apis/docs/reference/account-list.md): Retrieve list of user accounts and account IDs.
- [Account Balance](https://developer.webull.com/apis/docs/reference/account-balance.md): Query account balance, buying power, and cash details.
- [Account Positions](https://developer.webull.com/apis/docs/reference/account-position.md): Retrieve current positions and holdings.

### Order Management
- [Preview Order](https://developer.webull.com/apis/docs/reference/common-order-preview.md): Preview order details and estimated costs before placement.
- [Place Order](https://developer.webull.com/apis/docs/reference/common-order-place.md): Submit new orders for stocks, options, futures, or crypto.
- [Batch Place Orders](https://developer.webull.com/apis/docs/reference/order-batch-place.md): Submit multiple orders in a single batch request.
- [Replace Order](https://developer.webull.com/apis/docs/reference/common-order-replace.md): Modify existing open orders (price, quantity, etc.).
- [Cancel Order](https://developer.webull.com/apis/docs/reference/common-order-cancel.md): Cancel pending or open orders.
- [Order History](https://developer.webull.com/apis/docs/reference/order-history.md): Query historical order records and execution details.
- [Open Orders](https://developer.webull.com/apis/docs/reference/order-open.md): Retrieve list of current open orders.
- [Order Detail](https://developer.webull.com/apis/docs/reference/order-detail.md): Get detailed information for a specific order.

### Connect API (OAuth)
- [Connect API: Get Authorization Code](https://developer.webull.com/apis/docs/reference/connect-api/get-authorization-code.md): Initiate OAuth flow to obtain user authorization code.
- [Connect API: Create & Refresh Token](https://developer.webull.com/apis/docs/reference/connect-api/create-and-refresh-token.md): Exchange authorization code for access token and refresh expired tokens.

## Changelog
- [Documentation Changelog](https://developer.webull.com/apis/docs/changelog.md): Track updates, new features, and changes to the API documentation.

---

## Base URLs

### Production Environment
- HTTP API: `api.webull.com`
- Trading message push: `events-api.webull.com`
- Market data message push: `data-api.webull.com`

### Test Environment
- HTTP API: `us-openapi-alb.uat.webullbroker.com`
- Trading message push: `us-openapi-events.uat.webullbroker.com`

## Official SDKs

### Python
```bash
pip3 install --upgrade webull-openapi-python-sdk
```

### Java (Maven)
```xml
<dependency>
    <groupId>com.webull.openapi</groupId>
    <artifactId>webull-openapi-java-sdk</artifactId>
    <version>1.0.3</version>
</dependency>
```


---
id: about
---
# About Webull

### Introduction

Securities trading is offered to self-directed customers by Webull Financial LLC, a broker dealer registered with the Securities and Exchange Commission (SEC). Webull Financial LLC is a member of the Financial Industry Regulatory Authority (FINRA), Securities Investor Protection Corporation (SIPC), The New York Stock Exchange (NYSE), NASDAQ and Cboe EDGX Exchange, Inc (CBOE EDGX).

Webull is a customer-centric financial company, rooted in the internet and driven by technology at its core.


With years of experience in the internet and financial industries, the Webull team is committed to the deep integration of technology and finance, providing safe, professional, intelligent, and efficient products and services that let clients enjoy technology and enjoy investing.


We believe that individual investors are an important part of the market, not just “fodder.” Individual investors deserve better information, tools, services, trading opportunities, and trading costs. Respecting investors is respecting the market.

Machines are excellent assistants for human traders and will greatly augment human capabilities in trading hours, trading space, and trading technology. Algorithmic trading is an important trend for the future.

By empowering finance through technology, Webull provides a seamless one-stop self-directed investment platform and advanced intelligent investment tools for an excellent experience.


---
id: overview
title: Overview
---

# Introduction

The Trading API is divided into the Trade API and Data Events API, supporting trading and order status change subscriptions via HTTP and gRPC protocols. Its purpose is to provide investors with convenient, fast, and secure trading services.

To simplify the integration process, we provide SDKs for Python and JAVA. These SDKs are fully featured and enable developers to get started quickly.

**Main Features:**

Account Information: Query account balance and holdings information.

Trade Management: Create, modify, and cancel orders.

Subscribe to Real-Time Information: Subscribe to order status changes.


## Trading API Overview
<table>
<tr>
  <th>Type</th>
  <th>Function Overview</th>
  <th>Protocol</th>
  <th>Description</th>
  <th>Threshold</th>
</tr>
<tr>
    <td rowspan="5"><a href="/apis/docs/reference/instrument">Instruments</a></td>
    <td><a href="/apis/docs/reference/query-instruments">Get Instruments</a></td>
    <td>HTTP</td>
    <td>Retrieve a list of instruments for the given symbols</td>
    <td>10/30s</td>
</tr>
<tr>
    <td><a href="/apis/docs/reference/futures-instrument-list">Get Futures Contracts</a></td>
    <td>HTTP</td>
    <td>Retrieve futures contracts for the given symbols</td>
    <td>10/30s</td>
</tr>
<tr>
    <td><a href="/apis/docs/reference/query-instruments">Get Futures Contract By Code</a></td>
    <td>HTTP</td>
    <td>Retrieve a futures contract using the base code</td>
    <td>10/30s</td>
</tr>
<tr>
    <td><a href="/apis/docs/reference/futures-products">Get Futures Products</a></td>
    <td>HTTP</td>
    <td>Retrieve the list of available futures products for a specified market. </td>
    <td>10/30s</td>
</tr>
<tr>
    <td><a href="/apis/docs/reference/crypto-instrument-list">Get Crypto Instrument</a></td>
    <td>HTTP</td>
    <td>Retrieve a list of cryptocurrency instruments for the specified symbols</td>
    <td>10/30s</td>
</tr>
<tr>
  <td rowspan="3"><a href="/apis/docs/reference/instrument">Account</a></td>
  <td><a href="/apis/docs/reference/account">Account List</a></td>
  <td>HTTP</td>
  <td>Query account list</td>
  <td>10/30s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/account-balance">Account Balance</a></td>
  <td>HTTP</td>
  <td>Query account balance by account id</td>
  <td>2/2s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/account-position">Account Positions</a></td>
  <td>HTTP</td>
  <td>Query account position list by account id</td>
  <td>2/2s</td>
</tr>
<tr>
  <td rowspan="4"><a href="/apis/docs/reference/custom/order">Orders</a></td>
  <td><a href="/apis/docs/reference/common-order-preview">Estimate Orders</a></td>
  <td>HTTP</td>
  <td>Estimate the amount and cost for orders (supports stocks, options, futures, and crypto)</td>
  <td>150/10s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/common-order-place">Place Orders</a></td>
  <td>HTTP</td>
  <td>Place orders (supports stocks, options, futures, and crypto)</td>
  <td>600/60s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/option-replace">Replace Orders</a></td>
  <td>HTTP</td>
  <td>Replace existing orders (supports stocks, options, futures, and crypto)</td>
  <td>600/60s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/option-cancel">Cancel Order</a></td>
  <td>HTTP</td>
  <td>Cancel ordersusing the provided client_order_id (supports stocks, options, futures, and crypto)</td>
  <td>600/60s</td>
</tr>
<tr>
  <td rowspan="4"><a href="/apis/docs/reference/custom/order">Equity Order</a></td>
  <td><a href="/apis/docs/reference/preview-order">Estimate Equity Order</a></td>
  <td>HTTP</td>
  <td>Calculate the estimated order amount and associated costs based on the input information. Supports basic equity orders</td>
  <td>150/10s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/place-order">Place Equity Order</a></td>
  <td>HTTP</td>
  <td>Place equity orders</td>
  <td>600/60s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/replace-order">Replace Equity Order</a></td>
  <td>HTTP</td>
  <td>Modify equity orders</td>
  <td>600/60s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/cancel-order">Cancel Equity Order</a></td>
  <td>HTTP</td>
  <td>Cancel the equity order according to the incoming client_order_id</td>
  <td>600/60s</td>

</tr>
<tr>
  <td rowspan="4"><a href="/apis/docs/reference/custom/order">Option Order</a></td>
  <td><a href="/apis/docs/reference/option-preview">Estimate Option Order</a></td>
  <td>HTTP</td>
  <td>Calculate estimated amount and fees based on the input information, supporting general options orders</td>
  <td>150/10s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/option-place">Place Option Order</a></td>
  <td>HTTP</td>
  <td>Place options orders</td>
  <td>600/60s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/option-replace">Replace Option Order</a></td>
  <td>HTTP</td>
  <td>Modify existing options orders</td>
  <td>600/60s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/option-cancel">Cancel Option Order</a></td>
  <td>HTTP</td>
  <td>Cancel options orders using the provided client_order_id</td>
  <td>600/60s</td>
</tr>

<tr>
  <td rowspan="3"><a href="/apis/docs/reference/custom/order">Query Order</a></td>
  <td><a href="/apis/docs/reference/order-history">Query Historical Orders</a></td>
  <td>HTTP</td>
  <td>Retrieve historical order information, including both equities and options</td>
  <td>2/2s</td>
</tr>
<tr>
  <td><a href="/apis/docs/reference/order-open">Query Open Order</a></td>
  <td>HTTP</td>
  <td>Query pending orders by page</td>
  <td>2/2s</td>
</tr>
<tr>
 <td><a href="/apis/docs/reference/order-detail">Query Order Details</a></td>
  <td>HTTP</td>
  <td>Retrieve detailed information about specific orders, including both equities and options</td>
  <td>2/2s</td>
</tr>
<tr>
  <td rowspan="1"><a href="/apis/docs/reference/custom/order">Event</a></td>
  <td><a href="/apis/docs/reference/custom/subscribe-trade-events">Trading Event Subscription</a></td>
  <td>gRPC</td>
  <td>Subsccribe to receive live updates on order status changes</td>
  <td>\\</td>
</tr>
</table>


Test Accounts
The following information are for Trading API & Market Data API integration. You will no need to apply account seperately in test environment.

Note: since these accounts are shared publically, the orders and positions on the account may change. If you do need a seperate account for your testing, please reach out to our support team.

No. |	Test Account ID	| Test App Key	| Test Secret Key
1	| J6HA4EBQRQFJD2J6NQH0F7M649	| a88f2efed4dca02b9bc1a3cecbc35dba	| c2895b3526cc7c7588758351ddf425d6
2	| HBGQE8NM0CQG4Q34ABOM83HD09	| 6d9f1a0aa919a127697b567bb704369e	| adb8931f708ea3d57ec1486f10abf58c
3	| 4BJITU00JUIVEDO5V3PRA5C5G8	| eecbf4489f460ad2f7aecef37b267618	| 8abf920a9cc3cb7af3ea5e9e03850692