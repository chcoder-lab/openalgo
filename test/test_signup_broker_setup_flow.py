#!/usr/bin/env python3
"""Basic integration tests for signup and broker-setup flows.

Requires a running OpenAlgo server.
Set OPENALGO_BASE_URL to override the default URL.
"""

import os
import time

import pytest
import requests


BASE_URL = os.getenv("OPENALGO_BASE_URL", "http://127.0.0.1:5000")


def _server_available() -> bool:
    try:
        resp = requests.get(f"{BASE_URL}/auth/check-setup", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


@pytest.mark.skipif(not _server_available(), reason="OpenAlgo server is not running")
def test_signup_and_broker_setup_flow():
    session = requests.Session()

    setup_resp = session.get(f"{BASE_URL}/auth/check-setup")
    setup_resp.raise_for_status()
    setup_data = setup_resp.json()
    if setup_data.get("needs_setup"):
        pytest.skip("Initial setup required; create admin first")

    csrf_resp = session.get(f"{BASE_URL}/auth/csrf-token")
    csrf_resp.raise_for_status()
    csrf_token = csrf_resp.json().get("csrf_token")
    assert csrf_token

    ts = int(time.time())
    username = f"user_{ts}"
    email = f"user_{ts}@example.com"
    password = "StrongPass1!"

    signup_resp = session.post(
        f"{BASE_URL}/auth/signup",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
            "csrf_token": csrf_token,
        },
    )
    signup_resp.raise_for_status()
    signup_data = signup_resp.json()
    assert signup_data.get("status") == "success"

    creds_resp = session.get(f"{BASE_URL}/api/broker/credentials")
    creds_resp.raise_for_status()
    creds_data = creds_resp.json().get("data", {})
    brokers = creds_data.get("valid_brokers") or []
    assert brokers

    broker = brokers[0]
    redirect_url = f"{BASE_URL}/{broker}/callback"

    csrf_resp = session.get(f"{BASE_URL}/auth/csrf-token")
    csrf_resp.raise_for_status()
    csrf_token = csrf_resp.json().get("csrf_token")

    save_resp = session.post(
        f"{BASE_URL}/api/broker/credentials",
        data={
            "broker_api_key": "TESTKEY123456",
            "broker_api_secret": "TESTSECRET1234",
            "redirect_url": redirect_url,
            "csrf_token": csrf_token,
        },
        headers={"X-CSRFToken": csrf_token},
    )
    save_resp.raise_for_status()
    save_data = save_resp.json()
    assert save_data.get("status") == "success"

    verify_resp = session.get(f"{BASE_URL}/api/broker/credentials")
    verify_resp.raise_for_status()
    verify_data = verify_resp.json().get("data", {})
    assert verify_data.get("broker_api_key_raw_length") == len("TESTKEY123456")
