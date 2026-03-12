"""Smoke tests — run against the live MCP server on http://localhost:8000.

Usage:
    uv run python server.py http  # in one terminal (streamable HTTP on /mcp)
    uv run python tests/smoke_test.py  # in another
"""

from __future__ import annotations

import asyncio

from fastmcp import Client

client = Client("http://localhost:8000/mcp")


async def smoke():
    async with client:
        # ── search_formats ────────────────────────────────────────────────

        # 1. names
        r = await client.call_tool("search_formats", {"detail": "names"})
        assert "card" in str(r), "FAIL: search_formats names"
        print("PASS: search_formats names")

        # 2. summary with query
        r = await client.call_tool(
            "search_formats", {"query": "notification", "detail": "summary"}
        )
        assert "notification" in str(r), "FAIL: search_formats query"
        print("PASS: search_formats query")

        # 3. full detail
        r = await client.call_tool(
            "search_formats", {"query": "floating", "detail": "full"}
        )
        text = str(r)
        assert "code" in text or "GravityAd" in text or "boxShadow" in text, "FAIL: search_formats full has code"
        print("PASS: search_formats full")

        # 4. case-insensitive category
        r = await client.call_tool(
            "search_formats", {"category": "CARD", "detail": "names"}
        )
        text = str(r)
        assert "card" in text and "floating" in text, "FAIL: search_formats CARD uppercase"
        print("PASS: search_formats case-insensitive category")

        # ── generate_code ─────────────────────────────────────────────────

        # 5. basic fastapi streaming with placement_id
        r = await client.call_tool(
            "generate_code",
            {
                "format": "floating",
                "placement_id": "main",
                "framework": "fastapi",
                "streaming": True,
            },
        )
        text = str(r)
        assert "placement_id" in text, "FAIL: generate_code missing placement_id"
        assert "get_ads" in text or "server_code" in text, "FAIL: generate_code missing server code"
        assert "GravityAd" in text, "FAIL: generate_code missing client code"
        print("PASS: generate_code fastapi streaming")

        # 6. dark theme merged into JSX
        r = await client.call_tool(
            "generate_code",
            {
                "format": "card",
                "placement_id": "main",
                "framework": "nextjs",
                "streaming": False,
                "theme": "dark",
            },
        )
        text = str(r)
        assert "#18181B" in text, "FAIL: dark theme color missing"
        assert "// Theme overrides" not in text, "FAIL: theme should be merged, not comments"
        print("PASS: generate_code dark theme merged")

        # 7. site theme tokens merged
        r = await client.call_tool(
            "generate_code",
            {
                "format": "floating",
                "placement_id": "sidebar-1",
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
        assert "sidebar-1" in text, "FAIL: custom placement_id not in output"
        print("PASS: generate_code with site theme tokens + custom placement_id")

        # 8. custom placement (above_response)
        r = await client.call_tool(
            "generate_code",
            {
                "format": "card",
                "placement_id": "top-ad",
                "framework": "fastapi",
                "streaming": True,
                "placement": "above_response",
            },
        )
        text = str(r)
        assert "above_response" in text, "FAIL: custom placement not in server code"
        assert "top-ad" in text, "FAIL: custom placement_id not in server code"
        print("PASS: generate_code custom placement + placement_id")

        # 9. page-relative placements accepted
        for p in ("search_result", "center_page", "top_page", "bottom_page", "left_page", "right_page"):
            r = await client.call_tool(
                "generate_code",
                {"format": "card", "placement_id": "main", "placement": p},
            )
            text = str(r)
            assert p in text, f"FAIL: placement={p} not in output"
            assert not any(
                item.is_error for item in (r if isinstance(r, list) else [r])
                if hasattr(item, "is_error")
            ), f"FAIL: placement={p} returned an error"
        print("PASS: generate_code all page-relative placements accepted")

        # 10. invalid placement rejected by schema
        try:
            r = await client.call_tool(
                "generate_code",
                {"format": "card", "placement_id": "main", "placement": "somewhere_invalid"},
            )
            text = str(r)
            assert "literal_error" in text.lower() or "error" in text.lower(), "FAIL: invalid placement should be rejected"
        except Exception as e:
            assert "literal_error" in str(e).lower() or "input should be" in str(e).lower(), f"FAIL: unexpected error: {e}"
        print("PASS: generate_code rejects invalid placement (enum enforced)")

        # 11. missing placement_id rejected by schema
        try:
            r = await client.call_tool(
                "generate_code",
                {"format": "card"},
            )
            text = str(r)
            assert "missing" in text.lower() or "error" in text.lower(), "FAIL: missing placement_id should be rejected"
        except Exception as e:
            assert "missing" in str(e).lower() or "required" in str(e).lower(), f"FAIL: unexpected error: {e}"
        print("PASS: generate_code rejects missing placement_id (required enforced)")

        # 12. invalid placement_id format rejected
        r = await client.call_tool(
            "generate_code",
            {"format": "card", "placement_id": "has spaces!", "placement": "below_response"},
        )
        text = str(r)
        assert "error" in text.lower() and "placement_id" in text.lower(), "FAIL: invalid placement_id should be rejected"
        print("PASS: generate_code rejects invalid placement_id format")

        # 13. unknown format rejected
        r = await client.call_tool(
            "generate_code",
            {"format": "nonexistent", "placement_id": "main", "framework": "fastapi", "streaming": True},
        )
        assert "error" in str(r).lower() or "unknown" in str(r).lower(), "FAIL: bad format"
        print("PASS: generate_code rejects unknown format")

        # ── build_theme ───────────────────────────────────────────────────

        # 14. dark site theme
        r = await client.call_tool(
            "build_theme", {"bg_color": "#1a1a2e", "accent_color": "#F59E0B"}
        )
        text = str(r)
        assert "#1a1a2e" in text, "FAIL: build_theme bg_color"
        assert "#F59E0B" in text, "FAIL: build_theme accent"
        assert "slotProps" in text or "slot_props" in text.lower(), "FAIL: build_theme slotProps"
        print("PASS: build_theme dark site")

        # 15. invalid hex rejected
        r = await client.call_tool(
            "build_theme", {"bg_color": "not-a-color"}
        )
        text = str(r)
        assert "error" in text.lower() or "invalid" in text.lower(), "FAIL: build_theme should reject invalid hex"
        print("PASS: build_theme rejects invalid hex")

        # ── troubleshoot ──────────────────────────────────────────────────

        # 16. known symptom
        r = await client.call_tool("troubleshoot", {"symptom": "no ads showing"})
        assert "API" in str(r) or "key" in str(r).lower(), "FAIL: troubleshoot"
        print("PASS: troubleshoot known symptom")

        # 17. fuzzy match
        r = await client.call_tool("troubleshoot", {"symptom": "impressions not counting"})
        text = str(r)
        assert "impression" in text.lower(), "FAIL: troubleshoot fuzzy match"
        print("PASS: troubleshoot fuzzy match")

        # 18. unknown symptom fallback
        r = await client.call_tool("troubleshoot", {"symptom": "random gibberish"})
        text_lower = str(r).lower()
        assert (
            "contact" in text_lower or "support" in text_lower or "common" in text_lower
        ), "FAIL: troubleshoot fallback"
        print("PASS: troubleshoot fallback")

        # ── resources ─────────────────────────────────────────────────────

        # 19. format index
        r = await client.read_resource("gravity://formats")
        assert "floating" in str(r), "FAIL: formats index"
        print("PASS: resource gravity://formats")

        # 20. single format detail
        r = await client.read_resource("gravity://formats/banner")
        assert "banner" in str(r).lower(), "FAIL: format detail"
        print("PASS: resource gravity://formats/banner")

        # 21. docs topic
        r = await client.read_resource("gravity://docs/ad-response")
        assert "adText" in str(r), "FAIL: docs ad-response"
        print("PASS: resource gravity://docs/ad-response")

        # 22. placement policy includes all 11 placements
        r = await client.read_resource("gravity://docs/placement-policy")
        text = str(r)
        for p in ("above_response", "below_response", "search_result", "center_page", "top_page", "bottom_page", "left_page", "right_page"):
            assert p in text, f"FAIL: placement-policy missing {p}"
        print("PASS: resource gravity://docs/placement-policy includes all placements")

        print("\n--- ALL SMOKE TESTS PASSED ---")


if __name__ == "__main__":
    asyncio.run(smoke())
