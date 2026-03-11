import json

from broker.tastytrade.api.urls import get_tastytrade_base_url
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)


def _to_float(value, default=0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_quantity(value) -> float:
    if isinstance(value, dict):
        for key in ("quantity", "value", "amount", "number"):
            if key in value:
                return _to_float(value.get(key))
        return 0.0
    return _to_float(value)


def _apply_effect(value: float, effect: str | None) -> float:
    if not effect:
        return value
    effect = str(effect).lower()
    if effect == "debit":
        return -abs(value)
    if effect == "credit":
        return abs(value)
    return value

def get_trading_status(account_number: str, auth_token: str) -> dict | None:
    """
    Fetch trading status for a Tastytrade account.

    Args:
        account_number (str): Tastytrade account number
        auth_token (str): Bearer access token

    Returns:
        dict | None: Trading status data or None if error
    """
    url = f"{get_tastytrade_base_url()}/accounts/{account_number}/trading-status"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json"
    }
    try:
        client = get_httpx_client()
        response = client.get(url, headers=headers)
        response.raise_for_status()
        trading_status = response.json().get("data")
        logger.info(f"Fetched trading status for account {account_number}")
        return trading_status
    except Exception as e:
        logger.error(f"Error fetching trading status: {e}")
        return None


def get_accounts(auth_token: str) -> list[dict] | None:
    """
    Fetch all accounts for the authenticated Tastytrade user.

    Args:
        auth_token (str): Bearer access token

    Returns:
        list[dict] | None: List of account objects or None if error
    """
    url = f"{get_tastytrade_base_url()}/customers/me/accounts"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json"
    }
    try:
        client = get_httpx_client()
        response = client.get(url, headers=headers)
        response.raise_for_status()
        items = response.json().get("data", {}).get("items", [])
        logger.info(f"Fetched {len(items)} accounts for user")
        return items
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        return None


def _select_account_number(accounts: list[dict]) -> str | None:
    if not accounts:
        return None
    for account in accounts:
        account_data = account.get("account", {})
        if account_data.get("margin-or-cash") == "Margin":
            return account_data.get("account-number")
    return accounts[0].get("account", {}).get("account-number")


def _get_account_balances(account_number: str, auth_token: str) -> dict | None:
    url = f"{get_tastytrade_base_url()}/accounts/{account_number}/balances"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }
    try:
        client = get_httpx_client()
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error fetching balances: {e}")
        return None


def _get_account_positions(account_number: str, auth_token: str) -> list[dict]:
    url = f"{get_tastytrade_base_url()}/accounts/{account_number}/positions"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }
    try:
        client = get_httpx_client()
        response = client.get(url, headers=headers, params={"include-marks": "true"})
        response.raise_for_status()
        return response.json().get("data", {}).get("items", [])
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return []


def _extract_quote_price(quote: dict) -> float:
    for key in (
        "mark",
        "mid",
        "last",
        "lastExt",
        "lastMkt",
        "close",
        "prevClose",
        "dayClose",
        "dayClosePrice",
        "closePrice",
        "close-price",
        "mark-price",
        "markPrice",
        "midpoint",
        "mid-price",
        "midPrice",
        "last-price",
        "lastPrice",
    ):
        if key in quote:
            return _to_float(quote.get(key))

    bid = _to_float(
        quote.get("bid") or quote.get("bid-price") or quote.get("bidPrice")
    )
    ask = _to_float(
        quote.get("ask") or quote.get("ask-price") or quote.get("askPrice")
    )
    if bid and ask:
        return (bid + ask) / 2.0
    return 0.0


def _get_market_quotes(auth_token: str, positions: list[dict]) -> dict[str, float]:
    streamer_symbols = []
    symbols = []
    for position in positions:
        streamer_symbol = position.get("streamer-symbol")
        symbol = position.get("symbol")
        if streamer_symbol:
            streamer_symbols.append(streamer_symbol)
        if symbol:
            symbols.append(symbol)

    if not streamer_symbols and not symbols:
        return {}

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }
    client = get_httpx_client()
    quotes: dict[str, float] = {}

    if streamer_symbols:
        try:
            params = [("streamer-symbols", symbol) for symbol in streamer_symbols]
            response = client.get(
                f"{get_tastytrade_base_url()}/market-data/streamer-symbols/quotes",
                headers=headers,
                params=params,
            )
            if response.status_code < 400:
                payload = response.json()
                data = payload.get("data", payload)
                items = data.get("items") if isinstance(data, dict) else data
                if isinstance(items, list):
                    for item in items:
                        key = (
                            item.get("streamer-symbol")
                            or item.get("symbol")
                            or item.get("event-symbol")
                            or item.get("instrument", {}).get("symbol")
                            or item.get("instrumentKey", {}).get("symbol")
                        )
                        if key:
                            quotes[key] = _extract_quote_price(item)
        except Exception as e:
            logger.error(f"Error fetching market data for streamer symbols: {e}")

    if symbols:
        try:
            params = [("symbols", symbol) for symbol in symbols]
            response = client.get(
                f"{get_tastytrade_base_url()}/market-data/quotes",
                headers=headers,
                params=params,
            )
            if response.status_code < 400:
                payload = response.json()
                data = payload.get("data", payload)
                items = data.get("items") if isinstance(data, dict) else data
                if isinstance(items, list):
                    for item in items:
                        key = (
                            item.get("symbol")
                            or item.get("streamer-symbol")
                            or item.get("event-symbol")
                            or item.get("instrument", {}).get("symbol")
                            or item.get("instrumentKey", {}).get("symbol")
                        )
                        if key:
                            quotes[key] = _extract_quote_price(item)
        except Exception as e:
            logger.error(f"Error fetching market data for symbols: {e}")

    return quotes


def _calculate_positions_pnl(
    positions: list[dict], quotes: dict[str, float] | None = None
) -> tuple[float, float]:
    total_realized = 0.0
    total_unrealized = 0.0

    for position in positions:
        realized = _to_float(position.get("realized-today"))
        realized_effect = position.get("realized-today-effect")
        if realized == 0:
            realized = _to_float(position.get("realized-day-gain"))
            realized_effect = position.get("realized-day-gain-effect")
        total_realized += _apply_effect(realized, realized_effect)

        avg_open = _to_float(position.get("average-open-price"))
        qty = _to_quantity(position.get("quantity"))
        qty_direction = str(position.get("quantity-direction", "")).lower()

        price = 0.0
        if quotes:
            price = quotes.get(position.get("streamer-symbol")) or quotes.get(
                position.get("symbol")
            ) or 0.0

        if price == 0.0:
            price = (
                _to_float(position.get("mark"))
                or _to_float(position.get("mark-price"))
                or _to_float(position.get("close-price"))
            )

        if qty == 0 or avg_open == 0 or price == 0:
            continue

        if qty_direction == "short":
            total_unrealized += (avg_open - price) * qty
        else:
            total_unrealized += (price - avg_open) * qty

    return total_realized, total_unrealized


def get_margin_data(auth_token: str) -> dict:
    """
    Fetch margin data for the specified Tastytrade account.

    Args:
        auth_token (str): Bearer access token

    Returns:
        dict: Processed margin data in OpenAlgo format
    """
    default_response = {
        "availablecash": "0.00",
        "collateral": "0.00",
        "m2munrealized": "0.00",
        "m2mrealized": "0.00",
        "utiliseddebits": "0.00",
    }
    try:
        accounts = get_accounts(auth_token) or []
        account_number = _select_account_number(accounts)
        if not account_number:
            logger.error("No Tastytrade account number available for margin data")
            return default_response

        logger.info(f"Using account number: {account_number}")

        balances = _get_account_balances(account_number, auth_token) or {}
        positions = _get_account_positions(account_number, auth_token)
        quotes = _get_market_quotes(auth_token, positions)
        realized_pnl, unrealized_pnl = _calculate_positions_pnl(positions, quotes)

        availablecash = _to_float(
            balances.get("available-trading-funds"),
            default=_to_float(balances.get("cash-available-to-withdraw")),
        )
        if availablecash == 0:
            availablecash = _to_float(balances.get("cash-balance"))

        collateral = _to_float(balances.get("long-margineable-value"))
        if collateral == 0:
            collateral = _to_float(balances.get("long-equity-value"))

        utiliseddebits = _to_float(balances.get("maintenance-requirement"))
        if utiliseddebits == 0:
            utiliseddebits = _to_float(balances.get("reg-t-margin-requirement"))

        processed_margin_data = {
            "availablecash": f"{availablecash:.2f}",
            "collateral": f"{collateral:.2f}",
            "m2munrealized": f"{unrealized_pnl:.2f}",
            "m2mrealized": f"{realized_pnl:.2f}",
            "utiliseddebits": f"{utiliseddebits:.2f}",
        }

        return processed_margin_data

    except Exception as e:
        logger.info(f"Error processing margin data: {e}")
        return default_response
