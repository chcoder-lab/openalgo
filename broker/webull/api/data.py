import time
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


def _market_request(method: str, path: str, auth_token: str | None, query: dict | None = None):
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
        body=None,
        app_key=app_key,
        app_secret=app_secret,
    )

    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    client = get_httpx_client()
    response = client.request(method, url, headers=headers, params=query)
    response.raise_for_status()
    return response.json()


def _category_from_exchange(exchange: str) -> str:
    exchange_upper = (exchange or "").upper()
    if exchange_upper.startswith("FUT"):
        return "US_FUTURES"
    if exchange_upper.startswith("EVENT"):
        return "EVENT"
    return "US_STOCK"


def _epoch_ms(dt):
    return int(time.mktime(dt.timetuple()) * 1000)


class BrokerData:
    def __init__(self, auth_token, feed_token=None):
        self.auth_token = auth_token
        self.feed_token = feed_token

    def get_quotes(self, symbol: str, exchange: str) -> dict:
        category = _category_from_exchange(exchange)
        return _market_request(
            "GET",
            "/openapi/market-data/stock/snapshot",
            self.auth_token,
            query={"symbol": symbol, "category": category},
        )

    def get_depth(self, symbol: str, exchange: str) -> dict:
        category = _category_from_exchange(exchange)
        return _market_request(
            "GET",
            "/openapi/market-data/stock/quotes",
            self.auth_token,
            query={"symbol": symbol, "category": category},
        )

    def get_history(self, symbol, exchange, timeframe, from_date, to_date):
        category = _category_from_exchange(exchange)
        query = {
            "symbol": symbol,
            "category": category,
            "start_time": _epoch_ms(from_date),
            "end_time": _epoch_ms(to_date),
            "interval": timeframe,
        }
        return _market_request(
            "GET",
            "/openapi/market-data/stock/bars",
            self.auth_token,
            query=query,
        )


def get_stock_tick(auth_token: str, symbol: str, category: str = "US_STOCK"):
    return _market_request(
        "GET",
        "/openapi/market-data/stock/tick",
        auth_token,
        query={"symbol": symbol, "category": category},
    )


def get_stock_footprint(auth_token: str, symbol: str, category: str = "US_STOCK"):
    return _market_request(
        "GET",
        "/openapi/market-data/stock/footprint",
        auth_token,
        query={"symbol": symbol, "category": category},
    )


def get_stock_bars(
    auth_token: str,
    symbol: str,
    category: str,
    start_time: int,
    end_time: int,
    interval: str,
):
    return _market_request(
        "GET",
        "/openapi/market-data/stock/bars",
        auth_token,
        query={
            "symbol": symbol,
            "category": category,
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
        },
    )


def get_futures_tick(auth_token: str, symbol: str):
    return _market_request(
        "GET",
        "/openapi/market-data/futures/tick",
        auth_token,
        query={"symbol": symbol},
    )


def get_futures_snapshot(auth_token: str, symbol: str):
    return _market_request(
        "GET",
        "/openapi/market-data/futures/snapshot",
        auth_token,
        query={"symbol": symbol},
    )


def get_futures_footprint(auth_token: str, symbol: str):
    return _market_request(
        "GET",
        "/openapi/market-data/futures/footprint",
        auth_token,
        query={"symbol": symbol},
    )


def get_futures_depth(auth_token: str, symbol: str):
    return _market_request(
        "GET",
        "/openapi/market-data/futures/depth",
        auth_token,
        query={"symbol": symbol},
    )


def get_futures_historical_bars(auth_token: str, symbol: str, start_time: int, end_time: int):
    return _market_request(
        "GET",
        "/openapi/market-data/futures/bars",
        auth_token,
        query={"symbol": symbol, "start_time": start_time, "end_time": end_time},
    )


def get_event_snapshot(auth_token: str, symbol: str):
    return _market_request(
        "GET",
        "/openapi/market-data/event/snapshot",
        auth_token,
        query={"symbol": symbol},
    )


def get_event_depth(auth_token: str, symbol: str):
    return _market_request(
        "GET",
        "/openapi/market-data/event/depth",
        auth_token,
        query={"symbol": symbol},
    )
