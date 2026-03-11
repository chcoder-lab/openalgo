import os
from urllib.parse import urlencode

from broker.webull.api.signature import sign_request
from broker.webull.api.urls import get_webull_oauth_base_url, get_webull_token_base_url
from utils.config import (
    get_broker_api_key,
    get_broker_api_secret,
    get_broker_api_key_market,
    get_broker_api_secret_market,
    get_redirect_url,
)
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)


def _create_token() -> tuple[str | None, str | None]:
    try:
        app_key = get_broker_api_key_market()
        app_secret = get_broker_api_secret_market()
        if not app_key or not app_secret:
            return None, "Missing app_key/app_secret. Use Market API Key/Secret fields."

        token_url = f"{get_webull_token_base_url()}/openapi/auth/token/create"

        headers, _ = sign_request(
            method="POST",
            host=token_url.split("//", 1)[-1].split("/", 1)[0],
            path="/openapi/auth/token/create",
            query=None,
            body=None,
            app_key=app_key,
            app_secret=app_secret,
            extra_headers={"x-version": "v2"},
        )

        client = get_httpx_client()
        response = client.post(token_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        token = data.get("token") or data.get("access_token") or (data.get("data") or {}).get("token")
        if not token:
            return None, "Token not found in response."
        status = (data.get("status") or "").upper()
        if status and status != "APPROVED":
            return token, f"Token status is {status}. Verify via Webull App SMS before use."
        return token, None
    except Exception as e:
        logger.exception("Webull token create failed")
        return None, f"API error: {e}"


def authenticate_broker(
    authorization_code: str | None, redirect_uri: str | None = None
) -> tuple[str | None, str | None]:
    """
    Exchange authorization code for access token.
    """
    try:
        if authorization_code:
            client_id = get_broker_api_key()
            client_secret = get_broker_api_secret()

            if not client_id or not client_secret:
                return None, "Missing Webull client credentials. Configure Broker API Key and Secret."

            redirect_uri = redirect_uri or get_redirect_url()
            if not redirect_uri:
                return None, "Missing redirect URL. Configure Redirect URL in Profile > Broker."

            token_url = f"{get_webull_oauth_base_url()}/openapi/oauth2/token"
            payload = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            }

            client = get_httpx_client()
            response = client.post(
                token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                content=urlencode(payload),
            )

            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if not access_token:
                return None, "Access token not found in response."
            return access_token, None

        return _create_token()
    except Exception as e:
        logger.exception("Webull OAuth token exchange failed")
        return None, f"API error: {e}"
