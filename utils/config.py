# utils/config.py

import os
from contextvars import ContextVar

from dotenv import load_dotenv

# Load environment variables from .env file with override=True to ensure values are updated
load_dotenv(override=True)

_broker_context: ContextVar[dict | None] = ContextVar("broker_context", default=None)
_original_getenv = os.getenv
_broker_keys = {
    "BROKER_API_KEY",
    "BROKER_API_SECRET",
    "BROKER_API_KEY_MARKET",
    "BROKER_API_SECRET_MARKET",
    "REDIRECT_URL",
    "TASTYTRADE_ENV",
    "BROKER_API_ENV",
}


def _patched_getenv(key, default=None):
    if key in _broker_keys:
        ctx = _broker_context.get()
        if ctx and key in ctx and ctx[key] is not None:
            return ctx[key]
    return _original_getenv(key, default)


def ensure_getenv_patched():
    """Patch os.getenv to honor per-request broker context overrides."""
    if os.getenv is not _patched_getenv:
        os.getenv = _patched_getenv


def set_broker_context(context: dict) -> object:
    """Set broker context values for this execution context."""
    mapped = {}
    if context.get("broker_api_key") is not None:
        mapped["BROKER_API_KEY"] = context.get("broker_api_key")
    if context.get("broker_api_secret") is not None:
        mapped["BROKER_API_SECRET"] = context.get("broker_api_secret")
    if context.get("broker_api_key_market") is not None:
        mapped["BROKER_API_KEY_MARKET"] = context.get("broker_api_key_market")
    if context.get("broker_api_secret_market") is not None:
        mapped["BROKER_API_SECRET_MARKET"] = context.get("broker_api_secret_market")
    if context.get("redirect_url") is not None:
        mapped["REDIRECT_URL"] = context.get("redirect_url")
    if context.get("broker_api_environment") is not None:
        mapped["TASTYTRADE_ENV"] = context.get("broker_api_environment")
        mapped["BROKER_API_ENV"] = context.get("broker_api_environment")

    ensure_getenv_patched()
    return _broker_context.set(mapped)


def reset_broker_context(token: object) -> None:
    """Reset broker context to previous value."""
    _broker_context.reset(token)


def get_broker_api_key() -> str | None:
    """
    Retrieve the configured broker API key.

    Returns:
        str | None: The broker API key from environment variables, or None if not set.
    """
    return os.getenv("BROKER_API_KEY")


def get_broker_api_secret() -> str | None:
    """
    Retrieve the configured broker API secret.

    Returns:
        str | None: The broker API secret from environment variables, or None if not set.
    """
    return os.getenv("BROKER_API_SECRET")


def get_broker_api_key_market() -> str | None:
    return os.getenv("BROKER_API_KEY_MARKET")


def get_broker_api_secret_market() -> str | None:
    return os.getenv("BROKER_API_SECRET_MARKET")


def get_redirect_url() -> str | None:
    return os.getenv("REDIRECT_URL")


def get_login_rate_limit_min() -> str:
    """
    Retrieve the rate limit for logins per minute.

    Returns:
        str: The rate limit string (e.g., '5 per minute').
    """
    return os.getenv("LOGIN_RATE_LIMIT_MIN", "5 per minute")


def get_login_rate_limit_hour() -> str:
    """
    Retrieve the rate limit for logins per hour.

    Returns:
        str: The rate limit string (e.g., '25 per hour').
    """
    return os.getenv("LOGIN_RATE_LIMIT_HOUR", "25 per hour")


def get_host_server() -> str:
    """
    Retrieve the host server URL.

    Returns:
        str: The host server URL string.
    """
    return os.getenv("HOST_SERVER", "http://127.0.0.1:5000")
