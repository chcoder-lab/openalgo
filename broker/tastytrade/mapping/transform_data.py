# Mapping OpenAlgo API Request https://openalgo.in/docs
# Mapping tastytrade API https://developer.tastytrade.com

from database.token_db import get_br_symbol


# Map OpenAlgo exchange codes to tastytrade instrument types
INSTRUMENT_TYPE_MAP = {
    "EQUITY": "Equity",
    "OPTIONS": "Equity Option",
    "OPTION": "Equity Option",
    "EQUITY_OPTION": "Equity Option",
    "FUTURES": "Future",
    "FUTURE": "Future",
    "FUTURES_OPTION": "Future Option",
    "FUTURE_OPTION": "Future Option",
    "CRYPTO": "Cryptocurrency",
    "CRYPTOCURRENCY": "Cryptocurrency",
}

# tastytrade order types
ORDER_TYPE_MAP = {
    "MARKET": "Market",
    "LIMIT": "Limit",
    "SL": "Stop Limit",    # Stop-loss with limit price
    "SL-M": "Stop",        # Stop-loss market (stop trigger only)
}

# tastytrade time-in-force values
VALIDITY_MAP = {
    "DAY": "Day",
    "IOC": "IOC",
    "GTC": "GTC",
    "GTD": "GTD",
}

# Reverse map: tastytrade order type → OpenAlgo pricetype
REVERSE_ORDER_TYPE_MAP = {v: k for k, v in ORDER_TYPE_MAP.items()}

# Reverse map: tastytrade instrument type → OpenAlgo exchange code
REVERSE_INSTRUMENT_TYPE_MAP = {v: k for k, v in INSTRUMENT_TYPE_MAP.items()}


def map_instrument_type(exchange: str) -> str:
    """Map OpenAlgo exchange code to tastytrade instrument type."""
    return INSTRUMENT_TYPE_MAP.get(exchange.upper(), "Equity")


def map_order_type(pricetype: str) -> str:
    """Map OpenAlgo price type to tastytrade order type."""
    return ORDER_TYPE_MAP.get(pricetype.upper(), "Market")


def map_validity(validity: str) -> str:
    """Map OpenAlgo validity to tastytrade time-in-force."""
    return VALIDITY_MAP.get(validity.upper(), "Day")


def map_action(action: str) -> str:
    """
    Map OpenAlgo BUY/SELL to tastytrade leg action.

    tastytrade distinguishes Open/Close, but OpenAlgo does not.
    Default to Buy to Open / Sell to Close for directional trades.
    """
    return "Buy to Open" if action.upper() == "BUY" else "Sell to Close"


def map_product_type(product: str) -> str:
    """
    tastytrade does not have Indian-style product types (CNC/MIS/NRML).
    This maps them for internal display consistency only.
    """
    mapping = {"CNC": "Equity", "NRML": "Margin", "MIS": "Margin"}
    return mapping.get(product.upper(), "Equity")


def reverse_map_product_type(product: str) -> str:
    """Map tastytrade product context back to OpenAlgo product type."""
    mapping = {"equity": "CNC", "margin": "NRML"}
    return mapping.get(product.lower(), "CNC")


def transform_data(data: dict, token) -> dict:
    """
    Transform OpenAlgo order format to tastytrade legs-based API format.

    tastytrade orders use a 'legs' structure. Each leg specifies instrument-type,
    symbol, action (Buy to Open / Sell to Close), and quantity.

    Args:
        data: OpenAlgo order data dict
        token: Broker symbol token (used to look up broker symbol)

    Returns:
        dict: tastytrade order payload ready to POST to
              /accounts/{account-number}/orders
    """
    symbol = get_br_symbol(data["symbol"], data["exchange"])
    if not symbol:
        symbol = data["symbol"]

    action = map_action(data["action"])
    order_type = map_order_type(data["pricetype"])
    instrument_type = map_instrument_type(data["exchange"])

    leg = {
        "instrument-type": instrument_type,
        "symbol": symbol,
        "action": action,
        "quantity": int(data["quantity"]),
    }

    payload: dict = {
        "time-in-force": map_validity(data.get("validity", "DAY")),
        "order-type": order_type,
        "legs": [leg],
    }

    # Limit / Stop Limit orders require a price and price-effect
    if data["pricetype"] in ("LIMIT", "SL"):
        price = float(data.get("price", 0))
        if price:
            payload["price"] = str(price)
            payload["price-effect"] = "Debit" if data["action"].upper() == "BUY" else "Credit"

    # Stop / Stop Limit orders require a stop-trigger
    if data["pricetype"] in ("SL", "SL-M"):
        trigger = float(data.get("trigger_price", 0))
        if trigger:
            payload["stop-trigger"] = str(trigger)

    return payload


def transform_modify_order_data(data: dict, token) -> dict:
    """
    Transform OpenAlgo modify order format to tastytrade replace order payload.

    tastytrade replace uses PUT /accounts/{account-number}/orders/{order-id}
    with the same legs-based structure as place order.

    Args:
        data: OpenAlgo modify order data
        token: Broker symbol token

    Returns:
        dict: tastytrade replace-order payload
    """
    br_symbol = get_br_symbol(data["symbol"], data["exchange"])
    if not br_symbol:
        raise ValueError(f"Could not find broker symbol for {data['symbol']} on {data['exchange']}")

    quantity = int(data["quantity"])
    action = map_action(data["action"])
    order_type = map_order_type(data["pricetype"])
    instrument_type = map_instrument_type(data["exchange"])

    leg = {
        "instrument-type": instrument_type,
        "symbol": br_symbol,
        "action": action,
        "quantity": quantity,
    }

    payload: dict = {
        "time-in-force": map_validity(data.get("validity", "DAY")),
        "order-type": order_type,
        "legs": [leg],
    }

    if data["pricetype"] in ("LIMIT", "SL"):
        price = float(data.get("price", 0))
        if price:
            payload["price"] = str(price)
            payload["price-effect"] = "Debit" if data["action"].upper() == "BUY" else "Credit"

    if data["pricetype"] in ("SL", "SL-M"):
        trigger = float(data.get("trigger_price", 0))
        if trigger:
            payload["stop-trigger"] = str(trigger)

    return payload
