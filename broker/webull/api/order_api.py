import json
import uuid
from urllib.parse import urlparse

from broker.webull.api.signature import sign_request
from broker.webull.api.urls import get_webull_trade_base_url
from utils.config import get_broker_api_key_market, get_broker_api_secret_market
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)


def _get_app_credentials():
    app_key = get_broker_api_key_market()
    app_secret = get_broker_api_secret_market()
    if not app_key or not app_secret:
        raise ValueError(
            "Missing Webull app_key/app_secret. Use Market API Key/Secret fields."
        )
    return app_key, app_secret


def _request(method: str, path: str, auth_token: str | None, query: dict | None = None, body: dict | None = None):
    base_url = get_webull_trade_base_url()
    url = f"{base_url}{path}"
    parsed = urlparse(url)
    host = parsed.netloc

    app_key, app_secret = _get_app_credentials()
    headers, _ = sign_request(
        method=method,
        host=host,
        path=parsed.path,
        query=query,
        body=body,
        app_key=app_key,
        app_secret=app_secret,
    )

    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    client = get_httpx_client()
    response = client.request(method, url, headers=headers, params=query, json=body)

    if response.status_code == 404 and path.startswith("/openapi/"):
        fallback_path = path.replace("/openapi", "", 1)
        return _request(method, fallback_path, auth_token, query, body)

    response.raise_for_status()
    return response.json()


def _get_account_id(auth_token: str) -> str:
    data = _request("GET", "/openapi/account/list", auth_token)
    accounts = data.get("data") if isinstance(data, dict) else None
    if isinstance(accounts, list) and accounts:
        account_id = accounts[0].get("accountId") or accounts[0].get("account_id")
        if account_id:
            return str(account_id)
    raise RuntimeError("Account ID not found in Webull account list response.")


def _get_instrument_id(symbol: str, auth_token: str) -> str:
    query = {"symbol": symbol}
    data = _request("GET", "/openapi/instrument/list", auth_token, query=query)
    instruments = data.get("data") if isinstance(data, dict) else None
    if isinstance(instruments, list) and instruments:
        instrument_id = instruments[0].get("instrumentId") or instruments[0].get("instrument_id")
        if instrument_id:
            return str(instrument_id)
    raise RuntimeError(f"Instrument ID not found for symbol {symbol}.")


def get_order_book(auth):
    account_id = _get_account_id(auth)
    return _request("GET", "/openapi/trade/order/open", auth, query={"account_id": account_id})


def get_trade_book(auth):
    account_id = _get_account_id(auth)
    try:
        return _request(
            "GET",
            "/openapi/trade/order/history",
            auth,
            query={"account_id": account_id},
        )
    except Exception:
        return get_order_book(auth)


def get_positions(auth):
    account_id = _get_account_id(auth)
    return _request(
        "GET",
        "/openapi/assets/positions",
        auth,
        query={"account_id": account_id},
    )


def get_order_detail(auth, client_order_id: str):
    account_id = _get_account_id(auth)
    return _request(
        "GET",
        "/openapi/trade/order/detail",
        auth,
        query={"account_id": account_id, "client_order_id": client_order_id},
    )


def preview_order(auth, payload: dict):
    return _request("POST", "/openapi/trade/order/preview", auth, body=payload)


def get_holdings(auth):
    return get_positions(auth)


def get_open_position(tradingsymbol, exchange, product, auth):
    positions_data = get_positions(auth)
    net_qty = "0"
    if isinstance(positions_data, dict):
        positions = positions_data.get("data") or positions_data.get("positions") or []
        for position in positions:
            symbol = position.get("symbol") or position.get("ticker")
            qty = position.get("qty") or position.get("position") or position.get("quantity")
            if symbol == tradingsymbol and qty is not None:
                net_qty = str(qty)
                break
    return net_qty


def place_order_api(data, auth):
    try:
        account_id = _get_account_id(auth)
        symbol = data.get("symbol") or data.get("tradingsymbol")
        if not symbol:
            return False, {"status": "error", "message": "Symbol is required"}, None

        instrument_id = _get_instrument_id(symbol, auth)

        order_type = (data.get("order_type") or "MARKET").upper()
        order_type_map = {
            "MARKET": "MARKET",
            "LIMIT": "LIMIT",
            "SL": "STOP_LOSS_LIMIT",
            "SL-M": "STOP_LOSS",
        }
        mapped_type = order_type_map.get(order_type, "MARKET")

        side = (data.get("transaction_type") or "BUY").upper()
        tif = (data.get("validity") or "DAY").upper()
        if tif not in {"DAY", "GTC"}:
            tif = "DAY"

        stock_order = {
            "client_order_id": data.get("client_order_id") or uuid.uuid4().hex,
            "instrument_id": instrument_id,
            "order_type": mapped_type,
            "side": side,
            "tif": tif,
            "quantity": data.get("quantity"),
            "limit_price": data.get("price") or 0,
            "stop_price": data.get("trigger_price") or 0,
            "extended_hours_trading": bool(data.get("extended_hours", False)),
        }

        payload = {"account_id": account_id, "stock_order": stock_order}
        response = _request("POST", "/openapi/trade/order/place", auth, body=payload)

        order_id = None
        if isinstance(response, dict):
            order_id = (
                response.get("data", {}).get("order_id")
                or response.get("data", {}).get("orderId")
                or response.get("order_id")
            )

        return True, response, order_id
    except Exception as e:
        logger.exception("Webull place_order_api failed")
        return False, {"status": "error", "message": str(e)}, None


def place_smartorder_api(data, auth):
    return place_order_api(data, auth)


def cancel_all_orders_api(data, auth):
    try:
        account_id = _get_account_id(auth)
        open_orders = _request(
            "GET", "/openapi/trade/order/open", auth, query={"account_id": account_id}
        )
        orders = open_orders.get("data") if isinstance(open_orders, dict) else []
        results = []
        for order in orders or []:
            client_order_id = order.get("client_order_id") or order.get("clientOrderId")
            if not client_order_id:
                continue
            payload = {"account_id": account_id, "client_order_id": client_order_id}
            result = _request("POST", "/openapi/trade/order/cancel", auth, body=payload)
            results.append(result)
        return True, {"status": "success", "data": results}, None
    except Exception as e:
        logger.exception("Webull cancel_all_orders_api failed")
        return False, {"status": "error", "message": str(e)}, None
