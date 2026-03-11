from broker.webull.api.order_api import _get_account_id, _request
from utils.logging import get_logger

logger = get_logger(__name__)


def get_margin_data(auth_token: str) -> dict:
    """
    Fetch account balance/margin data for Webull.
    """
    try:
        account_id = _get_account_id(auth_token)
        data = _request(
            "GET",
            "/openapi/assets/balance",
            auth_token,
            query={"account_id": account_id},
        )
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.exception(f"Error fetching Webull balance: {e}")
        return {}
