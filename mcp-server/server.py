"""Gravity Ads Integration — FastMCP server entrypoint."""

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

mcp = FastMCP(
    "Gravity Ads Integration",
    instructions=(
        "Helps publishers integrate Gravity ads into FastAPI or Next.js apps. "
        "Provides ad format discovery, paired server+client code generation, "
        "and troubleshooting for common integration issues."
    ),
)


@mcp.custom_route("/health", ["GET"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, stateless_http=True)
