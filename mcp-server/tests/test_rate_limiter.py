"""Unit tests for the rate limiter module."""

from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from data.rate_limiter import (
    GENERATE_CODE_LIMIT,
    GLOBAL_LIMIT,
    TOOL_LIMIT,
    RateLimitExceeded,
    RateLimiter,
    check_rate_limit,
    get_limiter,
)


class TestRateLimiter:
    def _make(self, window: int = 60) -> RateLimiter:
        return RateLimiter(window_seconds=window)

    def test_allows_under_limit(self):
        rl = self._make()
        for _ in range(5):
            allowed, retry = rl.check("client:tool", max_requests=10)
            assert allowed is True
            assert retry == 0

    def test_blocks_at_limit(self):
        rl = self._make()
        for _ in range(3):
            rl.check("client:tool", max_requests=3)
        allowed, retry = rl.check("client:tool", max_requests=3)
        assert allowed is False
        assert retry >= 1

    def test_retry_after_is_positive(self):
        rl = self._make(window=10)
        for _ in range(2):
            rl.check("k", max_requests=2)
        _, retry = rl.check("k", max_requests=2)
        assert 1 <= retry <= 11

    def test_window_expires(self):
        rl = self._make(window=1)
        for _ in range(5):
            rl.check("k", max_requests=5)

        allowed, _ = rl.check("k", max_requests=5)
        assert allowed is False

        time.sleep(1.1)
        allowed, _ = rl.check("k", max_requests=5)
        assert allowed is True

    def test_separate_keys_are_independent(self):
        rl = self._make()
        for _ in range(3):
            rl.check("alice:tool", max_requests=3)
        blocked, _ = rl.check("alice:tool", max_requests=3)
        assert blocked is False

        allowed, _ = rl.check("bob:tool", max_requests=3)
        assert allowed is True

    def test_reset_single_key(self):
        rl = self._make()
        for _ in range(3):
            rl.check("k", max_requests=3)
        blocked, _ = rl.check("k", max_requests=3)
        assert blocked is False

        rl.reset("k")
        allowed, _ = rl.check("k", max_requests=3)
        assert allowed is True

    def test_reset_all(self):
        rl = self._make()
        for _ in range(3):
            rl.check("a", max_requests=3)
            rl.check("b", max_requests=3)
        rl.reset()
        allowed_a, _ = rl.check("a", max_requests=3)
        allowed_b, _ = rl.check("b", max_requests=3)
        assert allowed_a is True
        assert allowed_b is True

    def test_cleanup_removes_stale_buckets(self):
        rl = self._make(window=1)
        rl.check("stale", max_requests=10)
        time.sleep(1.1)

        rl._last_cleanup = 0
        rl._maybe_cleanup(time.monotonic())
        assert "stale" not in rl._buckets

    def test_thread_safety(self):
        rl = self._make(window=60)
        results: list[bool] = []
        lock = threading.Lock()

        def hammer():
            for _ in range(50):
                allowed, _ = rl.check("shared", max_requests=100)
                with lock:
                    results.append(allowed)

        threads = [threading.Thread(target=hammer) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        allowed_count = sum(1 for r in results if r)
        denied_count = sum(1 for r in results if not r)
        assert allowed_count == 100
        assert denied_count == 100


class TestCheckRateLimit:
    """Tests for the high-level check_rate_limit function."""

    def setup_method(self):
        get_limiter().reset()

    def test_passes_when_allowed(self):
        check_rate_limit("search_formats", "test-client")

    def test_raises_when_blocked(self):
        with patch("data.rate_limiter.TOOL_LIMIT", 2):
            check_rate_limit("search_formats", "c1")
            check_rate_limit("search_formats", "c1")
            with pytest.raises(RateLimitExceeded) as exc_info:
                check_rate_limit("search_formats", "c1")
            assert exc_info.value.retry_after >= 1
            assert "search_formats" in str(exc_info.value)

    def test_per_tool_limits_are_independent(self):
        with patch("data.rate_limiter.TOOL_LIMIT", 2):
            check_rate_limit("search_formats", "c1")
            check_rate_limit("search_formats", "c1")
            with pytest.raises(RateLimitExceeded):
                check_rate_limit("search_formats", "c1")

            check_rate_limit("troubleshoot", "c1")

    def test_global_limit_caps_across_tools(self):
        with patch("data.rate_limiter.GLOBAL_LIMIT", 5):
            for _ in range(3):
                check_rate_limit("search_formats", "c1")
            for _ in range(2):
                check_rate_limit("troubleshoot", "c1")

            with pytest.raises(RateLimitExceeded) as exc_info:
                check_rate_limit("search_formats", "c1")
            assert "Global rate limit" in str(exc_info.value)

    def test_different_clients_are_independent(self):
        with patch("data.rate_limiter.GENERATE_CODE_LIMIT", 2):
            check_rate_limit("generate_code", "alice")
            check_rate_limit("generate_code", "alice")
            with pytest.raises(RateLimitExceeded):
                check_rate_limit("generate_code", "alice")

            check_rate_limit("generate_code", "bob")

    def test_generate_code_has_stricter_limit(self):
        assert GENERATE_CODE_LIMIT < TOOL_LIMIT

    def test_exception_has_retry_after(self):
        with patch("data.rate_limiter.TOOL_LIMIT", 1):
            check_rate_limit("build_theme", "c1")
            with pytest.raises(RateLimitExceeded) as exc_info:
                check_rate_limit("build_theme", "c1")
            assert isinstance(exc_info.value.retry_after, int)
            assert exc_info.value.retry_after >= 1

    def test_default_constants(self):
        assert TOOL_LIMIT == 30
        assert GENERATE_CODE_LIMIT == 20
        assert GLOBAL_LIMIT == 60
