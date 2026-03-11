#!/usr/bin/env python3
"""Regression test ensuring broker credentials do not depend on .env variables."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import config as config_module


def test_broker_context_overrides_env(monkeypatch):
    # Ensure env vars are not set
    monkeypatch.delenv("BROKER_API_KEY", raising=False)
    monkeypatch.delenv("BROKER_API_SECRET", raising=False)
    monkeypatch.delenv("REDIRECT_URL", raising=False)

    config_module.ensure_getenv_patched()

    token = config_module.set_broker_context(
        {
            "broker_api_key": "KEY123",
            "broker_api_secret": "SECRET123",
            "redirect_url": "http://127.0.0.1:5000/zerodha/callback",
        }
    )

    try:
        assert os.getenv("BROKER_API_KEY") == "KEY123"
        assert os.getenv("BROKER_API_SECRET") == "SECRET123"
        assert os.getenv("REDIRECT_URL") == "http://127.0.0.1:5000/zerodha/callback"
    finally:
        config_module.reset_broker_context(token)
