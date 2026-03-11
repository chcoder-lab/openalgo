import httpx

from broker.tastytrade.api.urls import get_tastytrade_base_url
from utils.logging import get_logger

logger = get_logger(__name__)


def calculate_margin_api(positions, auth):
    """
    Calculate margin requirement for a basket of positions.

    Note: tastytrade does not provide a position-specific margin calculator API.
    The available Margin API only returns account-level margin information,
    which is not suitable for calculating margin requirements for specific positions.

    Args:
        positions: List of positions in OpenAlgo format
        auth: Authentication token for tastytrade

    Raises:
        NotImplementedError: tastytrade does not support position-specific margin calculator API
    """
    logger.warning("tastytrade does not provide position-specific margin calculator API")
    raise NotImplementedError("tastytrade does not support position-specific margin calculator API")


def get_account_margin(account_number: str, auth_token: str) -> dict | None:
    """
    Fetch margin requirements for a Tastytrade account.

    Args:
        account_number (str): Tastytrade account number
        auth_token (str): Bearer access token

    Returns:
        dict | None: Margin data or None if error
    """
    url = f"{get_tastytrade_base_url()}/margin/accounts/{account_number}/requirements"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json"
    }
    try:
        client = httpx.Client()
        response = client.get(url, headers=headers)
        response.raise_for_status()
        margin_data = response.json().get("data")
        logger.info(f"Fetched margin data for account {account_number}")
        return margin_data
    except Exception as e:
        logger.error(f"Error fetching margin data: {e}")
        return None
