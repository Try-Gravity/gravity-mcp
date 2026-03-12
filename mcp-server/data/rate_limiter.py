"""Sliding-window rate limiter for MCP tool calls.

Uses an in-memory sliding window log per (client, tool) pair.
Client identity is derived from the publisher API key hash when
available, falling back to "anonymous" for unauthenticated callers.

Limits:
    Per tool:       30 calls / 60s  (generate_code: 20 / 60s)
    Global (all):   60 calls / 60s
"""

from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)

WINDOW_SECONDS = 60
TOOL_LIMIT = 30
GENERATE_CODE_LIMIT = 20
GLOBAL_LIMIT = 60

_CLEANUP_INTERVAL = 300


class RateLimitExceeded(Exception):
    """Raised when a client exceeds their rate limit."""

    def __init__(self, message: str, retry_after: int) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class RateLimiter:
    """Thread-safe sliding-window rate limiter.

    Tracks timestamps of allowed requests in per-key buckets.
    A request is allowed only if the count of timestamps within
    the current window is below the limit.
    """

    def __init__(self, window_seconds: int = WINDOW_SECONDS) -> None:
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

    def check(self, key: str, max_requests: int) -> tuple[bool, int]:
        """Check whether a request is allowed under the rate limit.

        Returns (allowed, retry_after_seconds).
        retry_after_seconds is 0 when allowed, otherwise the number of
        seconds until the oldest request in the window expires.
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            self._maybe_cleanup(now)
            timestamps = self._buckets.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= max_requests:
                oldest = timestamps[0]
                retry_after = int(oldest + self.window_seconds - now) + 1
                self._buckets[key] = timestamps
                return False, max(retry_after, 1)

            timestamps.append(now)
            self._buckets[key] = timestamps
            return True, 0

    def _maybe_cleanup(self, now: float) -> None:
        """Remove buckets with no recent activity to bound memory."""
        if now - self._last_cleanup < _CLEANUP_INTERVAL:
            return
        self._last_cleanup = now
        cutoff = now - self.window_seconds
        stale = [k for k, ts in self._buckets.items() if not ts or ts[-1] <= cutoff]
        for k in stale:
            del self._buckets[k]
        if stale:
            logger.debug("Rate limiter cleanup: removed %d stale buckets", len(stale))

    def reset(self, key: str | None = None) -> None:
        """Clear rate limit state. Pass a key to clear one bucket, or None for all."""
        with self._lock:
            if key is None:
                self._buckets.clear()
            else:
                self._buckets.pop(key, None)


_limiter: RateLimiter | None = None


def get_limiter() -> RateLimiter:
    """Return the module-level RateLimiter singleton (lazy-init)."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter


def _tool_max(tool_name: str) -> int:
    return GENERATE_CODE_LIMIT if tool_name == "generate_code" else TOOL_LIMIT


def check_rate_limit(tool_name: str, client_id: str) -> None:
    """Check both per-tool and global rate limits for a client.

    Raises RateLimitExceeded if the client has exceeded their limit.
    FastMCP catches the exception and returns it as an is_error=True
    response, which works regardless of the tool's return type.
    """
    limiter = get_limiter()

    tool_max = _tool_max(tool_name)
    tool_key = f"{client_id}:{tool_name}"
    allowed, retry_after = limiter.check(tool_key, tool_max)
    if not allowed:
        logger.warning(
            "Rate limited: client=%s tool=%s (limit %d/%ds)",
            client_id, tool_name, tool_max, limiter.window_seconds,
        )
        raise RateLimitExceeded(
            f"Rate limit exceeded for {tool_name}. "
            f"Max {tool_max} requests per {limiter.window_seconds}s. "
            f"Retry after {retry_after}s.",
            retry_after=retry_after,
        )

    global_key = f"{client_id}:*"
    allowed, retry_after = limiter.check(global_key, GLOBAL_LIMIT)
    if not allowed:
        logger.warning(
            "Rate limited (global): client=%s (limit %d/%ds)",
            client_id, GLOBAL_LIMIT, limiter.window_seconds,
        )
        raise RateLimitExceeded(
            f"Global rate limit exceeded. "
            f"Max {GLOBAL_LIMIT} tool calls per {limiter.window_seconds}s. "
            f"Retry after {retry_after}s.",
            retry_after=retry_after,
        )
