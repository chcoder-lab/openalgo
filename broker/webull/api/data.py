from utils.logging import get_logger

logger = get_logger(__name__)


class BrokerData:
    def __init__(self, auth_token, feed_token=None):
        self.auth_token = auth_token
        self.feed_token = feed_token

    def get_quotes(self, symbol: str, exchange: str) -> dict:
        raise NotImplementedError("Webull OpenAPI market data is not supported.")

    def get_depth(self, symbol: str, exchange: str) -> dict:
        raise NotImplementedError("Webull OpenAPI market depth is not supported.")

    def get_history(self, symbol, exchange, timeframe, from_date, to_date):
        raise NotImplementedError("Webull OpenAPI historical data is not supported.")
