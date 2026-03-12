# Gravity MCP Server

FastMCP server that helps publishers integrate Gravity ads into **FastAPI** or **Next.js** applications. Provides ad format discovery, theme matching, paired server+client code generation, and troubleshooting.

## Quick start

### Prerequisites

```bash
# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Install and run

```bash
cd mcp-server
uv sync
uv run python server.py            # stdio transport (default, for Cursor)
uv run python server.py sse        # SSE on port 8000 (for remote clients)
```

### Docker

```bash
# From the repo root
cp .env.example .env
docker compose up --build -d

# Verify
curl http://localhost:8000/health    # → OK
curl http://localhost:8000/version   # → {"version":"0.2.0"}
docker compose logs -f               # watch logs
docker compose down                  # stop
```

The `placements` volume persists `placements.csv` across container restarts. The CSV auto-rotates at 10,000 rows.

## Tools

| Tool | Description |
|------|-------------|
| `search_formats` | Browse 25 ad formats with query/category filters and progressive detail levels |
| `build_theme` | Generate theme-matched style + slotProps from site design tokens (bg_color, accent_color, etc.) |
| `generate_code` | Generate paired FastAPI or Next.js server code + React client code with theme baked in |
| `troubleshoot` | Diagnose common integration issues from symptom descriptions (fuzzy + keyword matching) |

## Resources

| URI | Content |
|-----|---------|
| `gravity://formats` | Index of all 25 ad format names and descriptions |
| `gravity://formats/{name}` | Full detail for one format (code, type, omits) |
| `gravity://docs/{topic}` | SDK documentation by topic |

Doc topics: `ad-response`, `styling`, `react-component`, `server-sdk`, `js-sdk`, `placement-policy`, `checklist`

## Prompt

`integrate_gravity_ads(framework, format)` — step-by-step guide for integrating ads into a publisher's app. Automatically instructs the LLM to extract site theme tokens before generating code.

## Connect from Cursor (stdio)

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/gravity-mcp/mcp-server", "python", "server.py"]
    }
  }
}
```

Replace paths with your local values (`which uv` for the command). Restart Cursor to pick up changes.

## Testing

```bash
cd mcp-server

# Unit tests (no server needed)
uv run pytest tests/test_tools.py -v

# Smoke tests (server must be running on port 8000)
uv run python server.py sse &
uv run python tests/smoke_test.py
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Python log level (DEBUG, INFO, WARNING, ERROR) |
