"""End-to-end tests for GRAVITY_API_KEY auth flow.

Runs against the live MCP server on http://localhost:8000.

Usage:
    docker compose up --build -d
    uv run python tests/test_auth_e2e.py
"""

from __future__ import annotations

import asyncio
import json

from fastmcp import Client
from fastmcp.client.transports import SSETransport


async def test_no_key():
    """No API key → code generates but includes a warning."""
    client = Client("http://localhost:8000/mcp")
    async with client:
        r = await client.call_tool(
            "generate_code",
            {"format": "card", "placement_id": "test-no-key", "framework": "fastapi", "streaming": True},
        )
        text = str(r)
        assert "server_code" in text, "FAIL: no-key should still generate code"
        assert "warning" in text.lower(), "FAIL: no-key should include warning"
        assert "GRAVITY_API_KEY" in text, "FAIL: warning should mention GRAVITY_API_KEY"
    print("PASS: no API key → code generated with warning")


async def test_valid_key_header():
    """Valid API key via Authorization header → code generates without warning.

    We use a dummy key here since the validation gracefully degrades when the
    engine is unreachable or returns a non-401/403 response.
    """
    transport = SSETransport(
        "http://localhost:8000/mcp",
        headers={"Authorization": "Bearer test-valid-key-12345"},
    )
    client = Client(transport)
    async with client:
        r = await client.call_tool(
            "generate_code",
            {"format": "card", "placement_id": "test-valid", "framework": "nextjs", "streaming": False},
        )
        text = str(r)
        assert "server_code" in text, "FAIL: valid-key should generate code"
        assert "warning" not in text.lower(), "FAIL: valid-key should NOT have warning"
        assert "GRAVITY_API_KEY" in text, "FAIL: template should reference GRAVITY_API_KEY"
    print("PASS: valid API key via header → code generated, no warning")


async def test_template_references():
    """Generated templates should reference GRAVITY_API_KEY for all framework combos."""
    client = Client("http://localhost:8000/mcp")
    async with client:
        combos = [
            ("fastapi", True),
            ("fastapi", False),
            ("nextjs", True),
            ("nextjs", False),
        ]
        for framework, streaming in combos:
            r = await client.call_tool(
                "generate_code",
                {
                    "format": "card",
                    "placement_id": "template-test",
                    "framework": framework,
                    "streaming": streaming,
                },
            )
            text = str(r)
            assert "GRAVITY_API_KEY" in text, (
                f"FAIL: {framework}/streaming={streaming} template missing GRAVITY_API_KEY"
            )
    print("PASS: all framework/streaming combos reference GRAVITY_API_KEY")


async def test_db_has_publisher_key_hash():
    """When a key is provided, publisher_key_hash should be written to the DB."""
    import psycopg

    transport = SSETransport(
        "http://localhost:8000/mcp",
        headers={"Authorization": "Bearer db-test-key-xyz"},
    )
    client = Client(transport)
    async with client:
        r = await client.call_tool(
            "generate_code",
            {"format": "banner", "placement_id": "auth-db-test", "framework": "fastapi", "streaming": True},
        )

    conninfo = "postgresql://gravity:gravity@localhost:5432/gravity"
    with psycopg.connect(conninfo) as conn:
        row = conn.execute(
            "SELECT publisher_key_hash FROM placements WHERE placement_id = %s",
            ("auth-db-test",),
        ).fetchone()
        assert row is not None, "FAIL: placement not found in DB"
        assert row[0] != "", "FAIL: publisher_key_hash should not be empty"
        assert len(row[0]) == 16, f"FAIL: publisher_key_hash should be 16 chars, got {len(row[0])}"
    print("PASS: publisher_key_hash persisted to DB")


async def main():
    await test_no_key()
    await test_valid_key_header()
    await test_template_references()
    await test_db_has_publisher_key_hash()
    print("\n--- ALL AUTH E2E TESTS PASSED ---")


if __name__ == "__main__":
    asyncio.run(main())
