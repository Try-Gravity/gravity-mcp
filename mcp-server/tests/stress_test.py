"""Stress test — rapid-fire tool calls against the live MCP server.

Tests:
  1. Burst calls to each tool until rate-limited
  2. Burst generate_code (stricter limit)
  3. Concurrent calls across multiple tools to hit global limit
  4. Error response format under load
  5. Post-burst connectivity check

Usage:
    docker compose up --build -d
    uv run python tests/stress_test.py
"""

from __future__ import annotations

import asyncio
import time

from fastmcp import Client
from fastmcp.exceptions import ToolError

SERVER_URL = "http://localhost:8000/sse"


async def call_tool_safe(client: Client, tool: str, args: dict) -> tuple[str, str | None]:
    """Call a tool, returning ("ok", None) on success or ("limited", error_msg) on rate limit."""
    try:
        await client.call_tool(tool, args)
        return "ok", None
    except ToolError as e:
        msg = str(e)
        if "Rate limit" in msg or "rate limit" in msg:
            return "limited", msg
        return "error", msg
    except Exception as e:
        return "error", str(e)


async def stress_single_tool():
    """Burst calls to search_formats until rate-limited."""
    print("\n=== Test 1: Burst single tool (search_formats) ===")
    client = Client(SERVER_URL)
    async with client:
        successes = 0
        rate_limited = 0
        first_error = None

        for _ in range(40):
            status, msg = await call_tool_safe(client, "search_formats", {"detail": "names"})
            if status == "ok":
                successes += 1
            elif status == "limited":
                rate_limited += 1
                if first_error is None:
                    first_error = msg

        print(f"  Successes: {successes}")
        print(f"  Rate limited: {rate_limited}")
        assert successes >= 25, f"Expected >=25 successes before limit, got {successes}"
        assert rate_limited >= 1, "Expected at least 1 rate-limited response"
        if first_error:
            assert "Retry after" in first_error, f"Error should mention retry_after: {first_error}"
            print(f"  First error: {first_error[:100]}")
    print("PASS: single tool burst — rate limiting triggered correctly")


async def stress_generate_code():
    """Burst generate_code which has a stricter limit (20/60s)."""
    print("\n=== Test 2: Burst generate_code (stricter limit) ===")
    client = Client(SERVER_URL)
    async with client:
        successes = 0
        rate_limited = 0

        for i in range(30):
            status, _ = await call_tool_safe(client, "generate_code", {
                "format": "card",
                "placement_id": f"stress-{i}",
                "framework": "fastapi",
                "streaming": True,
            })
            if status == "ok":
                successes += 1
            elif status == "limited":
                rate_limited += 1

        print(f"  Successes: {successes}")
        print(f"  Rate limited: {rate_limited}")
        assert successes >= 1, f"Expected at least 1 success, got {successes}"
        assert rate_limited >= 1, "Expected rate limiting for generate_code"
        assert successes <= 20, \
            f"generate_code should enforce 20/min limit (got {successes} successes)"
    print("PASS: generate_code burst — stricter limit enforced")


async def stress_concurrent_tools():
    """Call multiple tools in rapid alternation to test global limit."""
    print("\n=== Test 3: Concurrent multi-tool burst (global limit) ===")
    client = Client(SERVER_URL)
    async with client:
        tools_and_args = [
            ("search_formats", {"detail": "names"}),
            ("build_theme", {"bg_color": "#1a1a2e"}),
            ("troubleshoot", {"symptom": "no ads"}),
            ("search_formats", {"query": "card", "detail": "summary"}),
            ("build_theme", {"accent_color": "#E11D48"}),
            ("troubleshoot", {"symptom": "CORS"}),
        ]

        successes = 0
        rate_limited = 0
        global_limited = 0

        for _ in range(15):
            for tool, args in tools_and_args:
                status, msg = await call_tool_safe(client, tool, args)
                if status == "ok":
                    successes += 1
                elif status == "limited":
                    if msg and "Global rate limit" in msg:
                        global_limited += 1
                    else:
                        rate_limited += 1

        total = successes + rate_limited + global_limited
        print(f"  Total calls: {total}")
        print(f"  Successes: {successes}")
        print(f"  Per-tool limited: {rate_limited}")
        print(f"  Global limited: {global_limited}")
        assert successes >= 1, f"Expected at least 1 success, got {successes}"
        assert rate_limited + global_limited >= 1, "Expected some rate limiting"
    print("PASS: multi-tool burst — global + per-tool limits enforced")


async def stress_error_format():
    """Verify rate limit errors are raised as ToolError with retry info."""
    print("\n=== Test 4: Error format under load ===")
    client = Client(SERVER_URL)
    async with client:
        errors: list[str] = []
        for _ in range(40):
            status, msg = await call_tool_safe(client, "build_theme", {"bg_color": "#000"})
            if status == "limited" and msg:
                errors.append(msg)

        assert len(errors) >= 1, "Need at least one rate-limit error to verify format"
        for e in errors:
            assert "Rate limit exceeded" in e or "Global rate limit" in e
            assert "Retry after" in e
        print(f"  Verified {len(errors)} error messages — all well-formed")
    print("PASS: error format consistent under load")


async def stress_recovery():
    """Verify the server still handles connections correctly after heavy load."""
    print("\n=== Test 5: Post-burst server health ===")
    client = Client(SERVER_URL)
    async with client:
        # Try troubleshoot — either succeeds or is rate-limited, both are fine
        status, msg = await call_tool_safe(client, "troubleshoot", {"symptom": "test recovery"})
        assert status in ("ok", "limited"), f"Unexpected status: {status}, msg: {msg}"

        # Resources are not rate-limited — should always work
        r = await client.read_resource("gravity://formats")
        assert "card" in str(r), "Resource should still work after burst"
    print("PASS: server healthy and responsive after stress test")


async def main():
    print("=" * 60)
    print("GRAVITY MCP SERVER — STRESS TEST")
    print("=" * 60)

    start = time.monotonic()

    await stress_single_tool()
    await stress_generate_code()
    await stress_concurrent_tools()
    await stress_error_format()
    await stress_recovery()

    elapsed = time.monotonic() - start
    print(f"\n{'=' * 60}")
    print(f"ALL STRESS TESTS PASSED ({elapsed:.1f}s)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
