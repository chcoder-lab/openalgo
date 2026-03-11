#!/usr/bin/env python3
"""Small Webull OpenAPI smoke test.

Usage example:
  python3 scripts/webull_smoke.py \
    --env sandbox \
    --token YOUR_ACCESS_TOKEN \
    --app-key YOUR_APP_KEY \
    --app-secret YOUR_APP_SECRET \
    --symbol AAPL
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from broker.webull.api.signature import sign_request
from broker.webull.api.urls import get_webull_trade_base_url


def _ms_epoch(seconds: float) -> int:
    return int(seconds * 1000)


def _pretty(obj: Any, limit: int = 2000) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=True)
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    token: str,
    app_key: str,
    app_secret: str,
    query: dict | None = None,
    body: dict | None = None,
) -> dict:
    base_url = get_webull_trade_base_url()
    url = f"{base_url}{path}"
    parsed = urlparse(url)
    host = parsed.netloc

    headers, _ = sign_request(
        method=method,
        host=host,
        path=parsed.path,
        query=query,
        body=body,
        app_key=app_key,
        app_secret=app_secret,
    )
    headers["Authorization"] = f"Bearer {token}"

    response = client.request(method, url, headers=headers, params=query, json=body)
    response.raise_for_status()
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Webull OpenAPI smoke test")
    parser.add_argument("--env", default="sandbox", choices=["sandbox", "production"])
    parser.add_argument("--token", required=True, help="Webull access token (Bearer)")
    parser.add_argument("--app-key", required=True, help="Webull app_key (for request signing)")
    parser.add_argument("--app-secret", required=True, help="Webull app_secret (for request signing)")
    parser.add_argument("--symbol", default="AAPL", help="Symbol for snapshot/quotes")
    parser.add_argument("--category", default="US_STOCK", help="Market data category")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--skip-bars", action="store_true", help="Skip bars endpoint")
    args = parser.parse_args()

    os.environ["BROKER_API_ENV"] = args.env

    with httpx.Client(timeout=args.timeout) as client:
        print(f"Base URL: {get_webull_trade_base_url()}")

        print("\n1) Account list")
        accounts = _request(
            client,
            "GET",
            "/openapi/account/list",
            token=args.token,
            app_key=args.app_key,
            app_secret=args.app_secret,
        )
        print(_pretty(accounts))

        account_id = None
        if isinstance(accounts, dict):
            data = accounts.get("data")
            if isinstance(data, list) and data:
                account_id = data[0].get("accountId") or data[0].get("account_id")

        if account_id:
            account_id = str(account_id)
            print("\n2) Account balance")
            balance = _request(
                client,
                "GET",
                "/openapi/assets/balance",
                token=args.token,
                app_key=args.app_key,
                app_secret=args.app_secret,
                query={"account_id": account_id},
            )
            print(_pretty(balance))

            print("\n3) Account positions")
            positions = _request(
                client,
                "GET",
                "/openapi/assets/positions",
                token=args.token,
                app_key=args.app_key,
                app_secret=args.app_secret,
                query={"account_id": account_id},
            )
            print(_pretty(positions))
        else:
            print("No account_id found in account list response; skipping balance/positions.")

        print("\n4) Stock snapshot")
        snapshot = _request(
            client,
            "GET",
            "/openapi/market-data/stock/snapshot",
            token=args.token,
            app_key=args.app_key,
            app_secret=args.app_secret,
            query={"symbol": args.symbol, "category": args.category},
        )
        print(_pretty(snapshot))

        print("\n5) Stock quotes")
        quotes = _request(
            client,
            "GET",
            "/openapi/market-data/stock/quotes",
            token=args.token,
            app_key=args.app_key,
            app_secret=args.app_secret,
            query={"symbol": args.symbol, "category": args.category},
        )
        print(_pretty(quotes))

        if not args.skip_bars:
            print("\n6) Stock bars")
            now = time.time()
            start_time = _ms_epoch(now - 3600)
            end_time = _ms_epoch(now)
            bars = _request(
                client,
                "GET",
                "/openapi/market-data/stock/bars",
                token=args.token,
                app_key=args.app_key,
                app_secret=args.app_secret,
                query={
                    "symbol": args.symbol,
                    "category": args.category,
                    "start_time": start_time,
                    "end_time": end_time,
                    "interval": "1m",
                },
            )
            print(_pretty(bars))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
