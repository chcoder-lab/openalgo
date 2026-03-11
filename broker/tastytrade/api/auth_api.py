import json
import os
from urllib.parse import urlencode

from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)

import hashlib

from broker.tastytrade.api.urls import get_tastytrade_base_url

from utils.httpx_client import get_httpx_client


def authenticate_broker(authorization_code: str, redirect_uri: str) -> tuple[str | None, str | None]:
    try:
        client_id = os.getenv("BROKER_API_KEY")
        client_secret = os.getenv("BROKER_API_SECRET")
        url = f"{get_tastytrade_base_url()}/oauth/token"

        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }

        client = get_httpx_client()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = client.post(url, data=data, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        if "access_token" in response_data:
            return response_data["access_token"], None
        else:
            return (
                None,
                "Authentication succeeded but no access token was returned. Please check the response.",
            )

    except Exception as e:
        error_message = str(e)
        try:
            if hasattr(e, "response") and e.response is not None:
                error_detail = e.response.json()
                error_message = error_detail.get("error_description", str(e))
        except Exception:
            pass
        return None, f"API error: {error_message}"
