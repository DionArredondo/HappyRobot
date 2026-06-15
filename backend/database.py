"""Supabase client initialization for the HappyRobot backend."""

from __future__ import annotations

import os

from supabase import Client, create_client

_SUPABASE_URL_ENV = "SUPABASE_URL"
_SUPABASE_KEY_ENV = "SUPABASE_KEY"


def _require_env(name: str) -> str:
    """Return a non-empty environment variable or raise a configuration error."""
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            "Verify that SUPABASE_URL and SUPABASE_KEY are defined in your local .env file."
        )
    return value.strip()


def _build_supabase_client() -> Client:
    """Construct the Supabase client from validated environment configuration."""
    supabase_url = _require_env(_SUPABASE_URL_ENV)
    supabase_key = _require_env(_SUPABASE_KEY_ENV)
    return create_client(supabase_url, supabase_key)


supabase: Client = _build_supabase_client()
