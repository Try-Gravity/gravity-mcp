"""Live JSX validation — calls generate_code for all 25 formats with themes.

Validates that every generated client_code:
  1. Has balanced braces (no }}}} or missing closers)
  2. Has no duplicate style= or slotProps= props
  3. Contains the theme colors when theme is applied
  4. Preserves format-specific layout props (maxWidth, display, etc.)

Usage:
    docker compose up --build -d
    uv run python tests/test_jsx_live.py
"""

from __future__ import annotations

import asyncio
import json
import re
import time

from fastmcp import Client
from fastmcp.exceptions import ToolError

SERVER_URL = "http://localhost:8000/sse"

ALL_FORMATS = [
    "card", "floating", "glass", "outlined", "tinted", "accent", "embed",
    "side-panel", "split-action", "labeled", "bubble", "compact-bar",
    "notification", "tooltip", "banner", "toolbar", "pill", "divider",
    "suggestion", "native", "quote", "minimal", "footnote",
    "text-link", "hyperlink",
]

FORMATS_WITH_LAYOUT_PROPS = {
    "notification": "maxWidth",
    "tooltip": "maxWidth",
    "side-panel": "maxWidth",
    "pill": "display",
    "bubble": "borderBottomLeftRadius",
    "quote": "paddingLeft",
    "banner": "width",
}


def check_balanced_braces(code: str, format_name: str) -> list[str]:
    """Check for balanced curly braces in JSX code."""
    errors = []
    depth = 0
    for i, ch in enumerate(code):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                errors.append(f"[{format_name}] Unmatched closing brace at position {i}")
                break
    if depth != 0:
        errors.append(f"[{format_name}] Unbalanced braces: depth ended at {depth}")

    if "}}}}" in code:
        errors.append(f"[{format_name}] Found quadruple closing braces }}}}}}}}")

    return errors


def check_no_duplicate_props(code: str, format_name: str) -> list[str]:
    """Check that style= and slotProps= don't appear more than once."""
    errors = []
    style_count = len(re.findall(r"\bstyle=\{\{", code))
    slot_count = len(re.findall(r"\bslotProps=\{\{", code))

    if "GravityAd" in code:
        if style_count > 1:
            errors.append(f"[{format_name}] Duplicate style= prop ({style_count} occurrences)")
        if slot_count > 1:
            errors.append(f"[{format_name}] Duplicate slotProps= prop ({slot_count} occurrences)")
    return errors


async def call_tool(client: Client, tool: str, args: dict) -> dict | None:
    """Call a tool, returning parsed dict or None if rate-limited."""
    try:
        r = await client.call_tool(tool, args)
    except ToolError as e:
        if "Rate limit" in str(e):
            return None
        raise
    content = getattr(r, "content", r)
    if isinstance(content, list):
        for item in content:
            text = getattr(item, "text", None)
            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass
        return {"_raw": str(r)}
    text = getattr(content, "text", str(content))
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"_raw": str(r)}


async def main():
    print("=" * 60)
    print("JSX VALIDITY TEST — ALL FORMATS × DARK THEME")
    print("=" * 60)

    start = time.monotonic()
    all_errors: list[str] = []
    passed = 0
    skipped = 0

    client = Client(SERVER_URL)
    async with client:
        for fmt in ALL_FORMATS:
            r = await call_tool(client, "generate_code", {
                "format": fmt,
                "placement_id": f"jsx-test-{fmt}",
                "framework": "fastapi",
                "streaming": True,
                "theme": "dark",
            })

            if r is None:
                skipped += 1
                print(f"  SKIP: {fmt} (rate-limited)")
                continue

            if "error" in r:
                all_errors.append(f"[{fmt}] Tool error: {r['error']}")
                continue

            client_code = r.get("client_code", "")
            if not client_code:
                all_errors.append(f"[{fmt}] No client_code in response")
                continue

            errors = check_balanced_braces(client_code, fmt)
            errors += check_no_duplicate_props(client_code, fmt)

            if "GravityAd" in client_code and fmt not in ("text-link", "hyperlink"):
                if "#18181B" not in client_code and "#18181b" not in client_code.lower():
                    errors.append(f"[{fmt}] Dark theme bg_color #18181B not found in client_code")

            if fmt in FORMATS_WITH_LAYOUT_PROPS:
                prop = FORMATS_WITH_LAYOUT_PROPS[fmt]
                if prop not in client_code:
                    errors.append(f"[{fmt}] Layout prop '{prop}' missing from themed client_code")

            if errors:
                all_errors.extend(errors)
                print(f"  FAIL: {fmt} — {len(errors)} error(s)")
                for e in errors:
                    print(f"        {e}")
            else:
                passed += 1
                print(f"  PASS: {fmt}")

        print(f"\n--- No-theme baseline (card, glass, notification) ---")
        for fmt in ["card", "glass", "notification"]:
            r = await call_tool(client, "generate_code", {
                "format": fmt,
                "placement_id": f"baseline-{fmt}",
                "framework": "nextjs",
                "streaming": False,
            })
            if r is None:
                skipped += 1
                print(f"  SKIP: {fmt} (no theme, rate-limited)")
                continue
            client_code = r.get("client_code", "")
            errors = check_balanced_braces(client_code, f"{fmt}-notheme")
            errors += check_no_duplicate_props(client_code, f"{fmt}-notheme")
            if errors:
                all_errors.extend(errors)
                print(f"  FAIL: {fmt} (no theme) — {len(errors)} error(s)")
            else:
                passed += 1
                print(f"  PASS: {fmt} (no theme)")

        print(f"\n--- Custom site tokens (glass — the bug reporter's format) ---")
        r = await call_tool(client, "generate_code", {
            "format": "glass",
            "placement_id": "glass-custom",
            "framework": "fastapi",
            "streaming": True,
            "bg_color": "#0f172a",
            "accent_color": "#38bdf8",
            "border_radius": 16,
            "font_family": "Inter, sans-serif",
        })
        if r is None:
            skipped += 1
            print(f"  SKIP: glass (custom tokens, rate-limited)")
        else:
            client_code = r.get("client_code", "")
            errors = check_balanced_braces(client_code, "glass-custom")
            errors += check_no_duplicate_props(client_code, "glass-custom")
            if "backdropFilter" not in client_code:
                errors.append("[glass-custom] Format-specific backdropFilter missing")
            if "#0f172a" not in client_code:
                errors.append("[glass-custom] Custom bg_color #0f172a missing")
            if "#38bdf8" not in client_code:
                errors.append("[glass-custom] Custom accent_color #38bdf8 missing")
            if errors:
                all_errors.extend(errors)
                print(f"  FAIL: glass (custom tokens) — {len(errors)} error(s)")
                for e in errors:
                    print(f"        {e}")
            else:
                passed += 1
                print(f"  PASS: glass (custom tokens)")

    elapsed = time.monotonic() - start

    print(f"\n{'=' * 60}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s), {passed} passed, {skipped} skipped ({elapsed:.1f}s)")
        for e in all_errors:
            print(f"  {e}")
        raise SystemExit(1)
    else:
        print(f"ALL {passed} JSX TESTS PASSED, {skipped} skipped due to rate limit ({elapsed:.1f}s)")
        assert passed >= 20, f"Expected at least 20 validated formats, got {passed}"
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
