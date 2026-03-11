import json

from broker.tastytrade.api.urls import get_tastytrade_base_url
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)


def calculate_pnl(entry):
    """Calculate realized and unrealized PnL for a given entry."""
    unrealized_pnl = (float(entry.get("lp", 0)) - float(entry.get("netavgprc", 0))) * float(
        entry.get("netqty", 0)
    )
    realized_pnl = (
        float(entry.get("daysellavgprc", 0)) - float(entry.get("daybuyavgprc", 0))
    ) * float(entry.get("daysellqty", 0))
    return realized_pnl, unrealized_pnl

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

def get_margin_data(auth_token: str) -> dict:
    """
    Fetch margin data for the specified Tastytrade account.

    Args:
        auth_token (str): Bearer access token

    Returns:
        dict: Processed margin data in OpenAlgo format
    """
    try:
        # Step 1: Set account number directly
        account_number = "5WY63601"
        logger.info(f"Using account number: {account_number}")

        # Step 2: Fetch margin requirements for this account
        url = f"{get_tastytrade_base_url()}/margin/accounts/{account_number}/requirements"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json"
        }
        client = get_httpx_client()
        response = client.get(url, headers=headers)
        response.raise_for_status()
        margin = response.json().get("data", {})

        # Step 3: Map tastytrade response to OpenAlgo format
        processed_margin_data = {
            "availablecash": "{:.2f}".format(float(margin.get("margin-equity", 0))),
            "collateral": "{:.2f}".format(float(margin.get("option-buying-power", 0))),
            "m2munrealized": "{:.2f}".format(float(margin.get("maintenance-excess", 0))),
            "utiliseddebits": "{:.2f}".format(float(margin.get("margin-requirement", 0))),
        }

        return processed_margin_data

    except Exception as e:
        logger.info(f"Error processing margin data: {e}")
        return {}
