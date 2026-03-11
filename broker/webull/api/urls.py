import os


SANDBOX_TRADE_BASE_URL = "http://us-openapi-alb.uat.webullbroker.com"
PRODUCTION_TRADE_BASE_URL = "https://api.webull.com"

SANDBOX_OAUTH_BASE_URL = "https://us-oauth-open-api.uat.webullbroker.com"
PRODUCTION_OAUTH_BASE_URL = "https://us-oauth-open-api.webull.com"

SANDBOX_OAUTH_LOGIN_BASE_URL = "https://passport.uat.webullbroker.com"
PRODUCTION_OAUTH_LOGIN_BASE_URL = "https://passport.webull.com"


def _normalize_env(value: str | None) -> str:
    if not value:
        return "sandbox"
    normalized = value.strip().lower()
    if normalized in {"prod", "production", "live"}:
        return "production"
    return "sandbox"


def get_webull_env() -> str:
    return _normalize_env(os.getenv("BROKER_API_ENV"))


def get_webull_trade_base_url() -> str:
    if get_webull_env() == "production":
        return PRODUCTION_TRADE_BASE_URL
    return SANDBOX_TRADE_BASE_URL


def get_webull_oauth_base_url() -> str:
    if get_webull_env() == "production":
        return PRODUCTION_OAUTH_BASE_URL
    return SANDBOX_OAUTH_BASE_URL


def get_webull_oauth_login_base_url() -> str:
    if get_webull_env() == "production":
        return PRODUCTION_OAUTH_LOGIN_BASE_URL
    return SANDBOX_OAUTH_LOGIN_BASE_URL


def get_webull_token_base_url() -> str:
    return get_webull_trade_base_url()
