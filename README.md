# Gravity MCP Server

An MCP (Model Context Protocol) server that helps publishers integrate [Gravity](https://trygravity.ai) ads into FastAPI and Next.js applications. Built with [FastMCP](https://github.com/jlowin/fastmcp).

## What it does

| Tool | Purpose |
|------|---------|
| `search_formats` | Browse 25 ad formats with query/category filters and progressive detail |
| `generate_code` | Generate paired server + client integration code with a unique `placement_id` |
| `troubleshoot` | Diagnose common integration issues from symptom descriptions |

The server also exposes `gravity://` resources for SDK documentation and a `integrate_gravity_ads` prompt template for guided integration.

## Quick start

### Native

```bash
cd mcp-server
uv sync
uv run python server.py
```

### Docker

```bash
docker compose up --build -d
curl http://localhost:8000/health   # → OK
```

MCP endpoint: `http://localhost:8000/mcp`

## Connect from Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Restart Cursor or reload MCP servers.

## Testing

```bash
cd mcp-server

# Unit tests
uv run pytest tests/ -v

# Smoke tests (server must be running on port 8000)
uv run python tests/smoke_test.py
```

See `test-guides/` for per-commit test gate instructions.

## Project structure

```
mcp-server/
  server.py                     # FastMCP entrypoint
  tools/
    search_formats.py           # Format discovery tool
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
    test_tools.py               # 17 unit tests
    smoke_test.py               # 12-step integration test
test-guides/                    # Per-commit test instructions
docker-compose.yml
```
