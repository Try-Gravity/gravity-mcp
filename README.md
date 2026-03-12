# Gravity MCP Server

An MCP (Model Context Protocol) server that helps publishers integrate [Gravity](https://trygravity.ai) ads into FastAPI and Next.js applications. Built with [FastMCP](https://github.com/jlowin/fastmcp).

## What it does

| Tool | Purpose |
|------|---------|
| `search_formats` | Browse 25 ad formats with query/category filters and progressive detail |
| `build_theme` | Generate theme-matched style + slotProps from site design tokens |
| `generate_code` | Generate paired server + client integration code with a unique `placement_id` |
| `troubleshoot` | Diagnose common integration issues from symptom descriptions |

The server also exposes `gravity://` resources for SDK documentation and an `integrate_gravity_ads` prompt template for guided integration.

## Quick start

### Native (stdio — for Cursor)

```bash
cd mcp-server
uv sync
uv run python server.py          # stdio transport (default)
```

### Native (HTTP — for remote clients)

```bash
uv run python server.py sse      # SSE on port 8000
```

### Docker

```bash
cp .env.example .env              # configure env vars
docker compose up --build -d
curl http://localhost:8000/health  # → OK
curl http://localhost:8000/version # → {"version":"0.2.0"}
```

## Connect from Cursor

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

Replace `/path/to/uv` with the output of `which uv` and `/path/to/gravity-mcp` with the repo location. Restart Cursor to load the server.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Python log level (DEBUG, INFO, WARNING, ERROR) |

## Testing

```bash
cd mcp-server

# Unit tests (no server needed)
uv run pytest tests/test_tools.py -v

# Smoke tests (start server first on port 8000)
uv run python server.py sse &
uv run python tests/smoke_test.py
```

## CI

GitHub Actions runs unit tests and a Docker health check on every push/PR to `main`. See `.github/workflows/ci.yml`.

## Project structure

```
mcp-server/
  server.py                     # FastMCP entrypoint (v0.2.0)
  tools/
    search_formats.py           # Format discovery tool
    build_theme.py              # Theme matching from design tokens
    generate_code.py            # Code generation + CSV registry
    troubleshoot.py             # Symptom-based diagnostics
  resources/
    format_catalog.py           # 25 ad format definitions
    docs.py                     # SDK documentation resources
  data/
    style_type_map.py           # Format name → SDK variant mapping
    troubleshoot_kb.py          # Curated symptom/cause/fix entries
  templates/
    fastapi_streaming.py        # FastAPI + SSE template
    fastapi_nonstreaming.py     # FastAPI + JSON template
    nextjs_streaming.py         # Next.js + SSE template
    nextjs_nonstreaming.py      # Next.js + JSON template
  tests/
    test_tools.py               # Unit tests
    smoke_test.py               # Integration tests (requires running server)
.github/workflows/ci.yml       # GitHub Actions CI
docker-compose.yml
.env.example
```
