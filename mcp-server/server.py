"""Gravity Ads Integration — FastMCP server entrypoint."""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from resources.docs import get_doc_topic, get_format_detail, get_formats_index
from tools.generate_code import generate_code as _generate_code
from tools.search_formats import search_formats as _search_formats

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
    return _search_formats(query=query, category=category, detail=detail)


@mcp.tool()
def generate_code(
    format: str,
    framework: Literal["fastapi", "nextjs"] = "fastapi",
    streaming: bool = True,
    theme: Literal["light", "dark"] | None = None,
    customizations: str | None = None,
) -> dict:
    """Generate paired server + client integration code for Gravity ads.

    Args:
        format: Ad format name (e.g. "floating", "card", "banner").
        framework: "fastapi" or "nextjs".
        streaming: True for SSE streaming, False for JSON response.
        theme: "dark" to include dark mode styling recipe.
        customizations: Natural language style notes (informational, for LLM context).
    """
    return _generate_code(
        format=format,
        framework=framework,
        streaming=streaming,
        theme=theme,
        customizations=customizations,
    )


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


# ── Health ───────────────────────────────────────────────────────────────────


@mcp.custom_route("/health", ["GET"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, stateless_http=True)
