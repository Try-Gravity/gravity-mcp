"""Smoke tests — run against the live MCP server on http://localhost:8000/mcp.

Usage:
    uv run python server.py  # in one terminal
    uv run python tests/smoke_test.py  # in another
"""

from __future__ import annotations

import asyncio
import csv
from pathlib import Path

from fastmcp import Client

client = Client("http://localhost:8000/mcp")


async def smoke():
    async with client:
        # 1. search_formats — names
        r = await client.call_tool("search_formats", {"detail": "names"})
        assert "card" in str(r), "FAIL: search_formats names"
        print("PASS: search_formats names")

        # 2. search_formats — summary with query
        r = await client.call_tool(
            "search_formats", {"query": "notification", "detail": "summary"}
        )
        assert "notification" in str(r), "FAIL: search_formats query"
        print("PASS: search_formats query")

        # 3. search_formats — full
        r = await client.call_tool(
            "search_formats", {"query": "floating", "detail": "full"}
        )
        text = str(r)
        assert "code" in text or "GravityAd" in text or "boxShadow" in text, "FAIL: search_formats full has code"
        print("PASS: search_formats full")

        # 4. generate_code — fastapi streaming
        r = await client.call_tool(
            "generate_code",
            {"format": "floating", "framework": "fastapi", "streaming": True},
        )
        text = str(r)
        assert "placement_id" in text, "FAIL: generate_code missing placement_id"
        assert "get_ads" in text or "server_code" in text, "FAIL: generate_code missing server code"
        assert "GravityAd" in text, "FAIL: generate_code missing client code"
        print("PASS: generate_code fastapi streaming")

        # 5. generate_code — dark theme
        r = await client.call_tool(
            "generate_code",
            {
                "format": "card",
                "framework": "nextjs",
                "streaming": False,
                "theme": "dark",
            },
        )
        assert "#18181B" in str(r) or "dark" in str(r).lower(), "FAIL: dark theme"
        print("PASS: generate_code dark theme")

        # 6. build_theme — dark site
        r = await client.call_tool(
            "build_theme", {"bg_color": "#1a1a2e", "accent_color": "#F59E0B"}
        )
        text = str(r)
        assert "#1a1a2e" in text, "FAIL: build_theme bg_color"
        assert "#F59E0B" in text, "FAIL: build_theme accent"
        assert "slotProps" in text or "slot_props" in text.lower(), "FAIL: build_theme slotProps"
        print("PASS: build_theme dark site")

        # 7. generate_code — with site theme tokens
        r = await client.call_tool(
            "generate_code",
            {
                "format": "floating",
                "framework": "fastapi",
                "streaming": True,
                "bg_color": "#0f172a",
                "accent_color": "#38bdf8",
                "border_radius": 12,
            },
        )
        text = str(r)
        assert "#0f172a" in text, "FAIL: site theme not in output"
        assert "theme_applied" in text, "FAIL: theme_applied missing"
        print("PASS: generate_code with site theme tokens")

        # 8. generate_code — unknown format rejected
        r = await client.call_tool(
            "generate_code",
            {"format": "nonexistent", "framework": "fastapi", "streaming": True},
        )
        assert "error" in str(r).lower() or "unknown" in str(r).lower(), "FAIL: bad format"
        print("PASS: generate_code rejects unknown format")

        # 9. troubleshoot — known symptom
        r = await client.call_tool("troubleshoot", {"symptom": "no ads showing"})
        assert "API" in str(r) or "key" in str(r).lower(), "FAIL: troubleshoot"
        print("PASS: troubleshoot known symptom")

        # 10. troubleshoot — unknown symptom
        r = await client.call_tool("troubleshoot", {"symptom": "random gibberish"})
        text_lower = str(r).lower()
        assert (
            "contact" in text_lower or "support" in text_lower or "common" in text_lower
        ), "FAIL: troubleshoot fallback"
        print("PASS: troubleshoot fallback")

        # 11. Read resource — format index
        r = await client.read_resource("gravity://formats")
        assert "floating" in str(r), "FAIL: formats index"
        print("PASS: resource gravity://formats")

        # 12. Read resource — single format
        r = await client.read_resource("gravity://formats/banner")
        assert "banner" in str(r).lower(), "FAIL: format detail"
        print("PASS: resource gravity://formats/banner")

        # 13. Read resource — docs topic
        r = await client.read_resource("gravity://docs/ad-response")
        assert "adText" in str(r), "FAIL: docs ad-response"
        print("PASS: resource gravity://docs/ad-response")

        # 14. Verify CSV was written
        csv_path = Path(__file__).parent.parent / "data" / "placements.csv"
        assert csv_path.exists(), "FAIL: placements.csv not created"
        with open(csv_path) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) >= 3, f"FAIL: expected at least 3 rows, got {len(rows)}"
        print(f"PASS: placements.csv has {len(rows)} rows")

        print("\n--- ALL SMOKE TESTS PASSED ---")


if __name__ == "__main__":
    asyncio.run(smoke())
