import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from urllib.parse import quote


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _md5_body(body: dict | None) -> str | None:
    if not body:
        return None
    payload = json.dumps(body, separators=(",", ":")).encode()
    return hashlib.md5(payload).hexdigest().upper()


def _build_param_string(params: dict) -> str:
    items = sorted((str(k), str(v)) for k, v in params.items())
    return "&".join([f"{k}={quote(v, safe='')}" for k, v in items])


def sign_request(
    *,
    method: str,
    host: str,
    path: str,
    query: dict | None,
    body: dict | None,
    app_key: str,
    app_secret: str,
    extra_headers: dict | None = None,
) -> tuple[dict, str]:
    """
    Sign a Webull OpenAPI request.

    Returns:
        headers dict and signature string
    """
    nonce = uuid.uuid4().hex
    timestamp = _iso_timestamp()
    signature_version = "1.0"
    signature_algorithm = "HMAC-SHA1"

    header_params = {
        "x-app-key": app_key,
        "x-signature-algorithm": signature_algorithm,
        "x-signature-version": signature_version,
        "x-signature-nonce": nonce,
        "x-timestamp": timestamp,
        "host": host,
    }
    if extra_headers:
        header_params.update({k.lower(): v for k, v in extra_headers.items()})

    params = {}
    if query:
        params.update(query)
    params.update(header_params)

    body_md5 = _md5_body(body)
    param_string = _build_param_string(params)

    sign_string = f"{path}&{param_string}"
    if body_md5:
        sign_string = f"{sign_string}&{body_md5}"

    encoded = quote(sign_string, safe="")
    secret_key = f"{app_secret}&".encode()
    signature = base64.b64encode(
        hmac.new(secret_key, encoded.encode(), hashlib.sha1).digest()
    ).decode()

    headers = {
        "x-app-key": app_key,
        "x-signature-algorithm": signature_algorithm,
        "x-signature-version": signature_version,
        "x-signature-nonce": nonce,
        "x-timestamp": timestamp,
        "Host": host,
        "Content-Type": "application/json",
        "x-signature": signature,
    }
    if extra_headers:
        headers.update(extra_headers)

    return headers, signature
