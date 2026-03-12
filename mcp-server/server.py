"""Gravity Ads Integration — FastMCP server entrypoint."""

from __future__ import annotations

import logging
import os
from typing import Literal

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from resources.docs import get_doc_topic, get_format_detail, get_formats_index
from tools.build_theme import build_theme as _build_theme
from tools.generate_code import generate_code as _generate_code
from tools.search_formats import search_formats as _search_formats
from tools.troubleshoot import troubleshoot as _troubleshoot

__version__ = "0.2.0"

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("gravity")

mcp = FastMCP(
    "Gravity Ads Integration",
    instructions=(
        "Helps publishers integrate Gravity ads into FastAPI or Next.js apps. "
        "Provides ad format discovery, paired server+client code generation, "
        "and troubleshooting for common integration issues."
    ),
)


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def search_formats(
    query: str | None = None,
    category: str | None = None,
    detail: Literal["names", "summary", "full"] = "summary",
) -> list:
    """Search available Gravity ad formats.

    Args:
        query: Keyword filter (substring match on name + description).
        category: Filter by SDK variant type (e.g. "card", "inline", "banner").
        detail: "names" for name list, "summary" for name/description/type, "full" includes code.
    """
    logger.info("search_formats query=%s category=%s detail=%s", query, category, detail)
    return _search_formats(query=query, category=category, detail=detail)


@mcp.tool()
def build_theme(
    bg_color: str | None = None,
    text_color: str | None = None,
    accent_color: str | None = None,
    secondary_color: str | None = None,
    border_color: str | None = None,
    border_radius: int | None = None,
    font_family: str | None = None,
) -> dict:
    """Build GravityAd style + slotProps that match the publisher's site theme.

    Pass design tokens extracted from the publisher's CSS, Tailwind config,
    or component styles. Omitted values are derived automatically — just
    passing bg_color is enough for a coherent theme.

    Args:
        bg_color: Site background color (e.g. "#FFFFFF", "#1a1a2e"). Drives dark/light detection.
        text_color: Primary text color. Auto-derived from bg_color if omitted.
        accent_color: Brand/accent color for CTA buttons.
        secondary_color: Muted text color for descriptions and labels.
        border_color: Border color for the ad container.
        border_radius: Border radius in pixels.
        font_family: CSS font-family string (e.g. "Inter, sans-serif").
    """
    logger.info("build_theme bg=%s accent=%s", bg_color, accent_color)
    return _build_theme(
        bg_color=bg_color,
        text_color=text_color,
        accent_color=accent_color,
        secondary_color=secondary_color,
        border_color=border_color,
        border_radius=border_radius,
        font_family=font_family,
    )


@mcp.tool()
def generate_code(
    format: str,
    framework: Literal["fastapi", "nextjs"] = "fastapi",
    streaming: bool = True,
    placement: str = "below_response",
    theme: Literal["light", "dark"] | None = None,
    bg_color: str | None = None,
    text_color: str | None = None,
    accent_color: str | None = None,
    secondary_color: str | None = None,
    border_color: str | None = None,
    border_radius: int | None = None,
    font_family: str | None = None,
) -> dict:
    """Generate paired server + client integration code for Gravity ads.

    Always pass site design tokens so the ad blends in natively. At minimum
    pass bg_color — all other colors are derived automatically.

    Args:
        format: Ad format name (e.g. "floating", "card", "banner").
        framework: "fastapi" or "nextjs".
        streaming: True for SSE streaming, False for JSON response.
        placement: Ad position relative to AI response. One of: above_response, below_response, inline_response, left_response, right_response.
        theme: Preset — "dark" auto-fills dark palette. Color params override preset.
        bg_color: Site background color. Drives automatic dark/light detection.
        text_color: Primary text color.
        accent_color: Brand/accent color for CTA buttons.
        secondary_color: Muted text color.
        border_color: Border color.
        border_radius: Border radius in pixels.
        font_family: CSS font-family string.
    """
    logger.info("generate_code format=%s fw=%s stream=%s placement=%s", format, framework, streaming, placement)
    return _generate_code(
        format=format,
        framework=framework,
        streaming=streaming,
        placement=placement,
        theme=theme,
        bg_color=bg_color,
        text_color=text_color,
        accent_color=accent_color,
        secondary_color=secondary_color,
        border_color=border_color,
        border_radius=border_radius,
        font_family=font_family,
    )


@mcp.tool()
def troubleshoot(symptom: str) -> dict:
    """Diagnose a Gravity ad integration issue.

    Args:
        symptom: Description of the problem (e.g. "no ads showing", "401", "CORS error").
    """
    logger.info("troubleshoot symptom=%s", symptom)
    return _troubleshoot(symptom=symptom)


# ── Resources ────────────────────────────────────────────────────────────────


@mcp.resource("gravity://formats")
def formats_index() -> str:
    """Index of all 25 Gravity ad formats with names and descriptions."""
    return get_formats_index()


@mcp.resource("gravity://formats/{name}")
def format_detail(name: str) -> str:
    """Full detail for a single ad format including code and omitted fields."""
    result = get_format_detail(name)
    if result is None:
        return f"Unknown format: {name}"
    return result


@mcp.resource("gravity://docs/{topic}")
def docs_topic(topic: str) -> str:
    """SDK documentation by topic: ad-response, styling, react-component, server-sdk, js-sdk, placement-policy, checklist."""
    result = get_doc_topic(topic)
    if result is None:
        available = "ad-response, styling, react-component, server-sdk, js-sdk, placement-policy, checklist"
        return f"Unknown topic: {topic}. Available topics: {available}"
    return result


# ── Prompts ──────────────────────────────────────────────────────────────────


@mcp.prompt()
def integrate_gravity_ads(framework: str = "fastapi", format: str = "card") -> str:
    """Step-by-step guide to integrate Gravity ads into a publisher's app."""
    return f"""\
You are helping a publisher integrate Gravity ads into their {framework} application.
The ad MUST blend seamlessly into the publisher's existing UI — even if they don't
explicitly ask for style matching. This is non-negotiable.

Follow these steps IN ORDER:

1. **Extract site theme** (MANDATORY — do this BEFORE generating code):
   Look at the publisher's codebase for design tokens. Check these sources:
   - Tailwind config (`tailwind.config.ts/js`) — look for `colors`, `borderRadius`, `fontFamily`
   - CSS variables in global stylesheets (e.g. `--background`, `--foreground`, `--primary`)
   - Component styles near the ad placement point (background, text color, border radius)
   - `globals.css`, `layout.tsx`, or theme provider files

   Extract at minimum: `bg_color` (background color where the ad will sit).
   Ideal: `bg_color`, `text_color`, `accent_color`, `border_radius`, `font_family`.

   You can call `build_theme` with these tokens to preview the resolved style and slotProps.

2. **Discover formats** — Call `search_formats` with `detail="summary"` to show
   available formats. If the publisher already chose "{format}", skip ahead.

3. **Generate code** — Call `generate_code` with:
   - `format="{format}"`
   - `framework="{framework}"`
   - `streaming=True` (or False for JSON responses)
   - **Always pass the extracted design tokens**: `bg_color`, `text_color`,
     `accent_color`, `border_radius`, `font_family` etc.
   - Use `theme="dark"` as a shortcut only if you cannot find specific colors
     but the site is clearly dark-themed.

   This returns paired server + client code with theme-matched styling built in.

4. **Verify the visual fit** — After generating code, review the `theme_applied`
   field in the result. Confirm:
   - The ad background matches or complements the site's background
   - Text colors have adequate contrast (WCAG AA)
   - The CTA button uses the site's accent/brand color
   - Border radius matches the site's component rounding
   - If the site uses a custom font, the ad inherits it

   If something looks off, call `generate_code` again with adjusted tokens.

5. **Verify integration** — Read the `gravity://docs/checklist` resource and walk
   through each item:
   - API key is set (GRAVITY_API_KEY env var)
   - Server-side fetch (not client-side)
   - gravityContext() sent from client
   - impUrl fires on ad visibility
   - clickUrl used for ad links (not url)
   - production: true when ready to go live

6. **Troubleshoot** — If the publisher reports issues, call `troubleshoot` with
   their symptom description.

Important:
- ALWAYS extract and pass site theme tokens. Never generate code without them.
- The `getAds()` / `get_ads()` function **never throws** — returns empty array on failure.
- Start the ad request early (before/alongside the LLM stream), await after streaming.
- Always use `ad.clickUrl` for links, not `ad.url`.
- Fire `ad.impUrl` within 5 minutes of receiving the ad.
"""


# ── Health ───────────────────────────────────────────────────────────────────


@mcp.custom_route("/health", ["GET"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.custom_route("/version", ["GET"])
async def version(request: Request) -> JSONResponse:
    return JSONResponse({"version": __version__})


if __name__ == "__main__":
    import sys

    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    logger.info("Starting Gravity MCP server v%s transport=%s", __version__, transport)
    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=8000, stateless_http=True)
    elif transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
    else:
        mcp.run(transport="stdio")
