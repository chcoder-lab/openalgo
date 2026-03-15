"""
tastytrade order management API.

All endpoints follow the tastytrade REST API:
  https://developer.tastytrade.com

Auth: OAuth2 Bearer token (Authorization: Bearer {access_token})
Base URL: https://api.tastyworks.com (production)
          https://api.cert.tastyworks.com (sandbox)
"""

import traceback
from typing import Optional

import httpx

from broker.tastytrade.api.funds import _select_account_number, get_accounts
from broker.tastytrade.api.urls import (
    ORDERS_API_VERSION,
    POSITIONS_API_VERSION,
    get_tastytrade_base_url,
)
from database.token_db import get_br_symbol, get_oa_symbol, get_token
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

from ..mapping.transform_data import (
    map_action,
    map_order_type,
    map_validity,
    reverse_map_product_type,
    transform_data,
    transform_modify_order_data,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bearer_headers(auth: str, version: str = None) -> dict:
    headers = {
        "Authorization": f"Bearer {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if version:
        headers["Accept-Version"] = version
    return headers


def _get_account_number(auth: str) -> Optional[str]:
    """Fetch and select the primary account number for this session."""
    accounts = get_accounts(auth)
    if not accounts:
        logger.error("No accounts found for the authenticated user")
        return None
    return _select_account_number(accounts)


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _to_int(value, default: int = 0) -> int:
    try:
        return int(float(value)) if value is not None else default
    except (TypeError, ValueError):
        return default


def _map_order_status(status: str) -> str:
    """Map tastytrade order status to OpenAlgo order_status."""
    status = (status or "").lower()
    if status in ("filled",):
        return "complete"
    if status in ("cancelled", "expired"):
        return "cancelled"
    if status in ("rejected",):
        return "rejected"
    # Received, Routed, In Flight, Live, Partially Filled, Contingent
    return "open"


def _map_leg_action(action: str) -> str:
    """Map tastytrade leg action to OpenAlgo BUY/SELL."""
    action = (action or "").lower()
    if "buy" in action:
        return "BUY"
    return "SELL"


def _map_order_type_reverse(order_type: str) -> str:
    """Map tastytrade order-type back to OpenAlgo pricetype."""
    mapping = {
        "Market": "MARKET",
        "Limit": "LIMIT",
        "Stop Limit": "SL",
        "Stop": "SL-M",
        "Notional Market": "MARKET",
    }
    return mapping.get(order_type, "MARKET")


def _instrument_type_to_exchange(instrument_type: str) -> str:
    """Map tastytrade instrument type to OpenAlgo exchange code."""
    mapping = {
        "Equity": "EQUITY",
        "Equity Option": "OPTIONS",
        "Future": "FUTURES",
        "Future Option": "FUTURES_OPTION",
        "Cryptocurrency": "CRYPTO",
    }
    return mapping.get(instrument_type, "EQUITY")


def _is_cancellable(status: str) -> bool:
    """Return True if the tastytrade order status allows cancellation."""
    return (status or "").lower() in (
        "received", "routed", "in flight", "live", "partially filled", "contingent"
    )


# ---------------------------------------------------------------------------
# Generic API request
# ---------------------------------------------------------------------------

def get_api_response(endpoint: str, auth: str, method: str = "GET",
                     data: dict = None, params: dict = None, version: str = None):
    """
    Make an authenticated request to the tastytrade REST API.

    Args:
        endpoint: Path relative to base URL (e.g. '/accounts/X/orders')
        auth: OAuth2 Bearer access token
        method: HTTP method (GET, POST, PUT, DELETE)
        data: JSON body for POST/PUT requests
        params: Query parameters for GET/DELETE requests
        version: Accept-Version header value (e.g. ORDERS_API_VERSION)

    Returns:
        dict: Parsed JSON response body, or {} for 204 No Content
    """
    headers = _bearer_headers(auth, version)
    client = get_httpx_client()
    url = f"{get_tastytrade_base_url()}{endpoint}"

    try:
        if method == "GET":
            response = client.get(url, headers=headers, params=params or data)
        elif method == "POST":
            response = client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = client.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json() if response.content else {}

    except Exception as e:
        logger.error(f"API request failed [{method} {url}]: {e}")
        raise


# ---------------------------------------------------------------------------
# Order Book
# ---------------------------------------------------------------------------

def get_order_book(auth: str) -> dict:
    """
    Fetch all orders for the account.

    Endpoint: GET /accounts/{account-number}/orders
    Returns orders in OpenAlgo format: {'stat': 'Ok', 'data': [...]}
    """
    try:
        account_number = _get_account_number(auth)
        if not account_number:
            return {"stat": "Not_Ok", "data": []}

        response = get_api_response(
            f"/accounts/{account_number}/orders",
            auth=auth,
            params={"per-page": 250},
            version=ORDERS_API_VERSION,
        )

        items = response.get("data", {}).get("items", [])
        transformed_orders = []

        for item in items:
            try:
                order = item.get("order", item)  # some responses nest under 'order'
                legs = order.get("legs", [])
                first_leg = legs[0] if legs else {}

                order_id = str(order.get("id", ""))
                action = _map_leg_action(first_leg.get("action", ""))
                symbol = first_leg.get("symbol", order.get("underlying-symbol", ""))
                instrument_type = first_leg.get("instrument-type",
                                                 order.get("underlying-instrument-type", "Equity"))
                exchange = _instrument_type_to_exchange(instrument_type)
                status = _map_order_status(order.get("status", ""))
                order_type = _map_order_type_reverse(order.get("order-type", "Market"))
                price = _to_float(order.get("price"))
                stop_trigger = _to_float(order.get("stop-trigger"))
                quantity = _to_int(first_leg.get("quantity", order.get("size", 0)))
                fill_qty = _to_int(first_leg.get("fill-quantity", 0))
                timestamp = order.get("updated-at", order.get("received-at", ""))

                openalgo_symbol = None
                try:
                    openalgo_symbol = get_oa_symbol(symbol, exchange)
                except Exception:
                    pass

                transformed_orders.append({
                    "stat": "Ok",
                    "data": {
                        "tradingsymbol": openalgo_symbol or symbol,
                        "exchange": exchange,
                        "quantity": quantity,
                        "side": action.lower(),
                        "type": order_type,
                        "order_id": order_id,
                        "order_time": timestamp,
                        "status": status,
                        "avg_price": _to_float(order.get("average-fill-price")),
                        "limit_price": price,
                        "stop_trigger": stop_trigger,
                        "fill_quantity": fill_qty,
                        "pending_quantity": quantity - fill_qty,
                        "validity": order.get("time-in-force", "Day"),
                        "cancellable": order.get("cancellable", False),
                    },
                })

            except Exception as e:
                logger.error(f"get_order_book - Error transforming order item: {e}")
                continue

        return {"stat": "Ok", "data": transformed_orders}

    except Exception as e:
        logger.error(f"get_order_book - {e}")
        logger.error(traceback.format_exc())
        return {"stat": "Not_Ok", "data": [], "message": str(e)}


# ---------------------------------------------------------------------------
# Trade Book
# ---------------------------------------------------------------------------

def get_trade_book(auth: str) -> list:
    """
    Fetch executed trades (transactions) for the account.

    Endpoint: GET /accounts/{account-number}/transactions?type[]=Trade
    Returns list of trades in OpenAlgo format.
    """
    try:
        account_number = _get_account_number(auth)
        if not account_number:
            return []

        response = get_api_response(
            f"/accounts/{account_number}/transactions",
            auth=auth,
            params={"type[]": "Trade", "per-page": 250},
        )

        items = response.get("data", {}).get("items", [])
        transformed_trades = []

        for txn in items:
            try:
                action = _map_leg_action(txn.get("action", ""))
                symbol = txn.get("symbol", txn.get("underlying-symbol", ""))
                instrument_type = txn.get("instrument-type", "Equity")
                exchange = _instrument_type_to_exchange(instrument_type)
                quantity = _to_int(_to_float(txn.get("quantity", 0)))
                price = _to_float(txn.get("price"))
                net_value = abs(_to_float(txn.get("net-value")))
                order_id = str(txn.get("order-id", txn.get("id", "")))
                timestamp = txn.get("executed-at", "")

                openalgo_symbol = None
                try:
                    openalgo_symbol = get_oa_symbol(symbol, exchange)
                except Exception:
                    pass

                transformed_trades.append({
                    "action": action,
                    "average_price": price,
                    "exchange": exchange,
                    "orderid": order_id,
                    "product": "CNC",
                    "quantity": quantity,
                    "symbol": openalgo_symbol or symbol,
                    "timestamp": timestamp,
                    "trade_value": net_value,
                })

            except Exception as e:
                logger.error(f"get_trade_book - Error transforming transaction: {e}")
                continue

        return transformed_trades

    except Exception as e:
        logger.error(f"get_trade_book - {e}")
        logger.error(traceback.format_exc())
        return []


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------

def get_positions(auth: str) -> dict:
    """
    Fetch open positions for the account.

    Endpoint: GET /accounts/{account-number}/positions?include-marks=true
    Returns: {'status': 'success', 'data': [...]} in OpenAlgo format
    """
    try:
        account_number = _get_account_number(auth)
        if not account_number:
            return {"status": "error", "message": "No account found"}

        response = get_api_response(
            f"/accounts/{account_number}/positions",
            auth=auth,
            params={"include-marks": "true"},
            version=POSITIONS_API_VERSION,
        )

        items = response.get("data", {}).get("items", [])
        positions_list = []

        for position in items:
            try:
                symbol = position.get("symbol", "")
                instrument_type = position.get("instrument-type", "Equity")
                exchange = _instrument_type_to_exchange(instrument_type)
                qty_direction = str(position.get("quantity-direction", "Long")).lower()
                quantity = _to_int(_to_float(position.get("quantity", 0)))

                if qty_direction == "short":
                    quantity = -quantity

                if quantity == 0:
                    continue

                avg_open = _to_float(position.get("average-open-price"))

                openalgo_symbol = None
                try:
                    openalgo_symbol = get_oa_symbol(symbol, exchange)
                except Exception:
                    pass

                positions_list.append({
                    "symbol": openalgo_symbol or symbol,
                    "exchange": exchange,
                    "product": "CNC",
                    "quantity": quantity,
                    "average_price": str(round(avg_open, 2)),
                })

            except Exception as e:
                logger.error(f"get_positions - Error transforming position: {e}")
                continue

        return {"status": "success", "data": positions_list}

    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        logger.error(f"get_positions - {e}")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Holdings
# ---------------------------------------------------------------------------

def get_holdings(auth: str) -> list:
    """
    Fetch equity holdings for the account.

    tastytrade does not have a dedicated holdings endpoint. This fetches all
    positions and returns long Equity positions as holdings.

    Endpoint: GET /accounts/{account-number}/positions?include-marks=true
    """
    try:
        account_number = _get_account_number(auth)
        if not account_number:
            return []

        response = get_api_response(
            f"/accounts/{account_number}/positions",
            auth=auth,
            params={"include-marks": "true"},
            version=POSITIONS_API_VERSION,
        )

        items = response.get("data", {}).get("items", [])
        holdings = []

        for position in items:
            try:
                instrument_type = position.get("instrument-type", "")
                if instrument_type != "Equity":
                    continue

                qty_direction = str(position.get("quantity-direction", "Long")).lower()
                quantity = _to_int(_to_float(position.get("quantity", 0)))
                if quantity <= 0 or qty_direction != "long":
                    continue

                symbol = position.get("symbol", "")
                avg_price = _to_float(position.get("average-open-price"))
                ltp = (
                    _to_float(position.get("mark"))
                    or _to_float(position.get("mark-price"))
                    or _to_float(position.get("close-price"))
                    or avg_price
                )

                pnl = (ltp - avg_price) * quantity
                pnl_percent = ((ltp - avg_price) / avg_price * 100) if avg_price else 0.0

                openalgo_symbol = None
                try:
                    openalgo_symbol = get_oa_symbol(symbol, "EQUITY")
                except Exception:
                    pass

                holdings.append({
                    "exchange": "EQUITY",
                    "pnl": round(pnl, 2),
                    "pnlpercent": round(pnl_percent, 2),
                    "product": "CNC",
                    "quantity": quantity,
                    "symbol": openalgo_symbol or symbol,
                    "avgprice": round(avg_price, 2),
                    "ltp": round(ltp, 2),
                })

            except Exception as e:
                logger.error(f"get_holdings - Error transforming position: {e}")
                continue

        return holdings

    except Exception as e:
        logger.error(f"get_holdings - {e}")
        return []


# ---------------------------------------------------------------------------
# Open Position Query
# ---------------------------------------------------------------------------

def get_open_position(tradingsymbol: str, exchange: str, producttype: str, auth: str) -> str:
    """
    Get net open position quantity for a specific symbol.

    Args:
        tradingsymbol: OpenAlgo symbol (e.g. 'AAPL')
        exchange: OpenAlgo exchange code (e.g. 'EQUITY')
        producttype: Product type (not used by tastytrade, kept for interface compat)
        auth: Bearer access token

    Returns:
        str: Net quantity ('5', '-3', '0', etc.)
    """
    try:
        tradingsymbol = str(tradingsymbol).upper().strip()
        exchange = str(exchange).upper().strip()

        positions_response = get_positions(auth)
        if not positions_response or positions_response.get("status") != "success":
            return "0"

        for position in positions_response.get("data", []):
            pos_symbol = str(position.get("symbol", "")).upper().strip()
            pos_exch = str(position.get("exchange", "")).upper().strip()
            pos_qty = _to_int(position.get("quantity", 0))

            # Match on symbol; also try with exchange if provided
            symbol_match = pos_symbol == tradingsymbol
            exch_match = not exchange or pos_exch == exchange or exchange == "EQUITY"

            if symbol_match and exch_match and pos_qty != 0:
                return str(pos_qty)

        return "0"

    except Exception as e:
        logger.error(f"get_open_position - {e}")
        return "0"


# ---------------------------------------------------------------------------
# Place Order
# ---------------------------------------------------------------------------

def place_order_api(data: dict, auth: str) -> tuple:
    """
    Place an order via tastytrade.

    Endpoint: POST /accounts/{account-number}/orders
    Payload uses tastytrade legs-based JSON format.

    Returns:
        tuple: (response_obj, response_data, order_id)
    """
    try:
        required = ["symbol", "exchange", "action", "quantity", "pricetype"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            msg = f"Missing required fields: {', '.join(missing)}"
            return None, {"status": "error", "message": msg}, None

        account_number = _get_account_number(auth)
        if not account_number:
            return None, {"status": "error", "message": "No account found"}, None

        token = get_token(data["symbol"], data["exchange"])
        payload = transform_data(data, token)

        client = get_httpx_client()
        url = f"{get_tastytrade_base_url()}/accounts/{account_number}/orders"

        response = client.post(url, headers=_bearer_headers(auth, ORDERS_API_VERSION), json=payload, timeout=30.0)
        response.raise_for_status()
        response_data = response.json()

        order = response_data.get("data", {}).get("order", {})
        order_id = str(order.get("id", ""))

        if not order_id:
            logger.warning(f"place_order_api - No order ID in response: {response_data}")
            return None, {"status": "error", "message": "No order ID returned"}, None

        class _Resp:
            def __init__(self, code):
                self.status = code

        return (
            _Resp(response.status_code),
            {"status": "success", "orderid": order_id},
            order_id,
        )

    except httpx.HTTPStatusError as e:
        msg = f"HTTP {e.response.status_code}"
        try:
            err = e.response.json()
            msg = err.get("error", {}).get("message", msg)
        except Exception:
            msg = e.response.text or msg
        logger.error(f"place_order_api - {msg}")
        return None, {"status": "error", "message": msg}, None

    except Exception as e:
        logger.error(f"place_order_api - {e}")
        logger.error(traceback.format_exc())
        return None, {"status": "error", "message": str(e)}, None


# ---------------------------------------------------------------------------
# Smart Order
# ---------------------------------------------------------------------------

def place_smartorder_api(data: dict, auth: str) -> tuple:
    """
    Place a smart order that adjusts to the target position size.

    position_size=0 → square off all
    position_size>0 → target long position
    position_size<0 → target short position
    """
    try:
        symbol = data.get("symbol")
        exchange = data.get("exchange")
        product = data.get("product", "CNC")

        try:
            position_size = int(float(data.get("position_size", "0")))
        except (ValueError, TypeError):
            return None, {"status": "error", "message": "Invalid position_size"}, None

        current_position = int(float(get_open_position(symbol, exchange, product, auth) or 0))

        final_action = None
        final_quantity = 0

        if position_size == 0:
            if current_position > 0:
                final_action, final_quantity = "SELL", current_position
            elif current_position < 0:
                final_action, final_quantity = "BUY", abs(current_position)
            else:
                return None, {"status": "success", "orderid": ""}, ""

        elif current_position == 0:
            if position_size > 0:
                final_action, final_quantity = "BUY", position_size
            elif position_size < 0:
                final_action, final_quantity = "SELL", abs(position_size)
            else:
                return None, {"status": "success", "orderid": ""}, ""

        else:
            if position_size > current_position:
                final_action = "BUY"
                final_quantity = position_size - current_position
            elif position_size < current_position:
                final_action = "SELL"
                final_quantity = current_position - position_size
            else:
                return None, {"status": "success", "orderid": ""}, ""

        if not final_action or final_quantity <= 0:
            return None, {"status": "error", "message": "No valid action determined"}, None

        order_data = {**data, "action": final_action, "quantity": str(final_quantity)}
        res, response, orderid = place_order_api(order_data, auth)

        if response and response.get("status") == "success" and orderid:
            return res, {"status": "success", "orderid": str(orderid)}, orderid

        return None, {"status": "error", "message": response.get("message", "Order failed")}, None

    except Exception as e:
        logger.error(f"place_smartorder_api - {e}")
        return None, {"status": "error", "message": str(e)}, None


# ---------------------------------------------------------------------------
# Cancel Order
# ---------------------------------------------------------------------------

def cancel_order(orderid: str, auth: str) -> tuple:
    """
    Cancel an open order.

    Endpoint: DELETE /accounts/{account-number}/orders/{order-id}
    tastytrade returns 204 No Content on success.
    """
    try:
        account_number = _get_account_number(auth)
        if not account_number:
            return {"stat": "Not_Ok", "data": {"msg": "No account found"}}, 400

        client = get_httpx_client()
        url = f"{get_tastytrade_base_url()}/accounts/{account_number}/orders/{orderid}"
        response = client.delete(url, headers=_bearer_headers(auth, ORDERS_API_VERSION))
        response.raise_for_status()

        return {
            "stat": "Ok",
            "data": {"msg": "Order cancelled successfully", "order_id": orderid},
        }, 200

    except httpx.HTTPStatusError as e:
        msg = f"HTTP {e.response.status_code}"
        try:
            err = e.response.json()
            msg = err.get("error", {}).get("message", msg)
        except Exception:
            pass
        return {"stat": "Not_Ok", "data": {"msg": msg}}, e.response.status_code

    except Exception as e:
        logger.error(f"cancel_order - {e}")
        return {"stat": "Not_Ok", "data": {"msg": str(e)}}, 500


def cancel_all_orders_api(data: dict, auth: str) -> tuple:
    """Cancel all cancellable open orders."""
    try:
        order_book = get_order_book(auth)
        if order_book.get("stat") != "Ok":
            return [], []

        orders = order_book.get("data", [])
        canceled = []
        failed = []

        for order in orders:
            order_data = order.get("data", order)
            order_id = str(order_data.get("order_id", ""))
            if not order_id:
                continue
            if not order_data.get("cancellable", False):
                continue

            try:
                cancel_resp, status_code = cancel_order(order_id, auth)
                if status_code in (200, 204):
                    canceled.append(order_id)
                else:
                    failed.append({"orderId": order_id, "error": cancel_resp.get("data", {}).get("msg", "Unknown")})
            except Exception as e:
                failed.append({"orderId": order_id, "error": str(e)})

        return canceled, failed

    except Exception as e:
        logger.error(f"cancel_all_orders_api - {e}")
        return [], []


# ---------------------------------------------------------------------------
# Modify Order
# ---------------------------------------------------------------------------

def modify_order(data: dict, auth: str) -> tuple:
    """
    Replace (modify) an existing order.

    Endpoint: PUT /accounts/{account-number}/orders/{order-id}
    Uses the same legs-based JSON as place order.
    """
    try:
        order_id = data.get("orderid")
        if not order_id:
            return {"stat": "Not_Ok", "data": {"msg": "Missing orderid"}}, 400

        account_number = _get_account_number(auth)
        if not account_number:
            return {"stat": "Not_Ok", "data": {"msg": "No account found"}}, 400

        token = get_token(data["symbol"], data["exchange"])
        payload = transform_modify_order_data(data, token)

        client = get_httpx_client()
        url = f"{get_tastytrade_base_url()}/accounts/{account_number}/orders/{order_id}"
        response = client.put(url, headers=_bearer_headers(auth, ORDERS_API_VERSION), json=payload, timeout=30.0)
        response.raise_for_status()

        resp_data = response.json()
        new_order = resp_data.get("data", {}).get("order", {})
        new_order_id = str(new_order.get("id", order_id))

        return {
            "stat": "Ok",
            "data": {"msg": "Order modified successfully", "order_id": new_order_id},
        }, 200

    except httpx.HTTPStatusError as e:
        msg = f"HTTP {e.response.status_code}"
        try:
            err = e.response.json()
            msg = err.get("error", {}).get("message", msg)
        except Exception:
            pass
        return {"stat": "Not_Ok", "data": {"msg": msg}}, e.response.status_code

    except Exception as e:
        logger.error(f"modify_order - {e}")
        return {"stat": "Not_Ok", "data": {"msg": str(e)}}, 500


# ---------------------------------------------------------------------------
# Close All Positions
# ---------------------------------------------------------------------------

def close_all_positions(current_api_key: str, auth: str) -> tuple:
    """Close all open positions by placing offsetting market orders."""
    try:
        positions_response = get_positions(auth)

        if (
            not positions_response
            or positions_response.get("status") != "success"
            or not positions_response.get("data")
        ):
            return {"status": "success", "message": "No open positions found"}, 200

        success_count = 0
        failed_count = 0

        for position in positions_response.get("data", []):
            try:
                quantity = int(position.get("quantity", 0))
                if quantity == 0:
                    continue

                action = "SELL" if quantity > 0 else "BUY"
                symbol = position.get("symbol")
                exchange = position.get("exchange", "EQUITY")

                if not symbol:
                    failed_count += 1
                    continue

                order_data = {
                    "apikey": current_api_key,
                    "strategy": "Squareoff",
                    "symbol": symbol,
                    "action": action,
                    "exchange": exchange,
                    "pricetype": "MARKET",
                    "product": position.get("product", "CNC"),
                    "quantity": str(abs(quantity)),
                }

                _, response, orderid = place_order_api(order_data, auth)

                if response.get("status") == "success" and orderid:
                    success_count += 1
                else:
                    logger.error(f"close_all_positions - Failed for {symbol}: {response.get('message')}")
                    failed_count += 1

            except Exception as e:
                logger.error(f"close_all_positions - Error for {position}: {e}")
                failed_count += 1

        if success_count > 0 or failed_count == 0:
            return {"status": "success", "message": "All Open Positions SquaredOff"}, 200
        else:
            return {
                "status": "error",
                "message": f"Closed {success_count}, failed {failed_count}",
            }, 400

    except Exception as e:
        logger.error(f"close_all_positions - {e}")
        return {"status": "error", "message": str(e)}, 500
