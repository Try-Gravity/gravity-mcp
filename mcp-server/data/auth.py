"""API key extraction, validation, and hashing for publisher auth."""

from __future__ import annotations

import hashlib
import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)

_ENGINE_URL = "https://server.trygravity.ai/api/v1/ad"
_CACHE_TTL_SECONDS = 300  # 5 minutes
_cache: dict[str, float] = {}  # key_hash -> expiry timestamp


def get_api_key() -> str | None:
    """Extract the publisher API key from the request header or env var.

    SSE/HTTP transport: reads Authorization: Bearer <key> header.
    stdio transport: reads GRAVITY_API_KEY env var.
    """
    try:
        from fastmcp.server.dependencies import get_http_headers

        headers = get_http_headers(include_all=True)
        if headers:
            auth = headers.get("authorization", "")
            if auth.lower().startswith("bearer "):
                return auth.split(" ", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get("GRAVITY_API_KEY") or None


def hash_key(key: str) -> str:
    """SHA-256 hash of the API key, truncated to 16 hex chars."""
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def validate_api_key(key: str) -> bool:
    """Validate a publisher API key by probing the Gravity engine.

    Returns True if the key is valid, False if 401/403.
    Caches successful validations for 5 minutes.
    Falls back to True if the engine is unreachable (graceful degradation).
    """
    key_h = hash_key(key)

    expiry = _cache.get(key_h)
    if expiry and time.monotonic() < expiry:
        return True

    try:
        resp = httpx.post(
            _ENGINE_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={"messages": [], "placements": []},
            timeout=5.0,
        )
        if resp.status_code in (401, 403):
            logger.warning("API key validation failed: %s", resp.status_code)
            return False

        _cache[key_h] = time.monotonic() + _CACHE_TTL_SECONDS
        return True
    except Exception:
        logger.warning("Engine unreachable for key validation — allowing request")
        _cache[key_h] = time.monotonic() + _CACHE_TTL_SECONDS
        return True
