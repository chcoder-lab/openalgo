import os
from urllib.parse import urlparse


SANDBOX_BASE_URL = "https://api.cert.tastyworks.com"
SANDBOX_STREAMER_HOST = "streamer.cert.tastyworks.com"
PRODUCTION_BASE_URL = "https://api.tastyworks.com"
PRODUCTION_STREAMER_HOST = "streamer.tastyworks.com"


def _normalize_env(value: str | None) -> str:
    if not value:
        return "sandbox"
    normalized = value.strip().lower()
    if normalized in {"prod", "production", "live"}:
        return "production"
    return "sandbox"


def get_tastytrade_env() -> str:
    return _normalize_env(os.getenv("TASTYTRADE_ENV"))


def get_tastytrade_base_url() -> str:
    if get_tastytrade_env() == "production":
        return PRODUCTION_BASE_URL
    return SANDBOX_BASE_URL


def get_tastytrade_streamer_host() -> str:
    if get_tastytrade_env() == "production":
        return PRODUCTION_STREAMER_HOST
    return SANDBOX_STREAMER_HOST


def get_tastytrade_base_host() -> str:
    base_url = get_tastytrade_base_url()
    parsed = urlparse(base_url)
    return parsed.netloc or base_url.replace("https://", "").replace("http://", "")
