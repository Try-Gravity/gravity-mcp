# Gravity MCP Server

FastMCP server that helps publishers integrate Gravity ads into **FastAPI** or **Next.js** applications. Provides ad format discovery, paired server+client code generation, and troubleshooting.

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
uv run python server.py
```

The server starts on `http://0.0.0.0:8000`. MCP endpoint at `http://localhost:8000/mcp`.

### Docker

```bash
# From the repo root
docker compose up --build -d

# Verify
curl http://localhost:8000/health   # → OK
docker compose logs -f              # watch logs
docker compose down                 # stop
```

The `data/` directory is mounted as a volume so `placements.csv` persists across restarts.

## Tools

| Tool | Description |
|------|-------------|
| `search_formats` | Browse 25 ad formats with query/category filters and progressive detail levels |
| `generate_code` | Generate paired FastAPI or Next.js server code + React client code with a unique `placement_id` |
| `troubleshoot` | Diagnose common integration issues from symptom descriptions |

## Resources

| URI | Content |
|-----|---------|
| `gravity://formats` | Index of all 25 ad format names and descriptions |
| `gravity://formats/{name}` | Full detail for one format (code, type, omits) |
| `gravity://docs/{topic}` | SDK documentation by topic |

Doc topics: `ad-response`, `styling`, `react-component`, `server-sdk`, `js-sdk`, `placement-policy`, `checklist`

## Prompt

`integrate_gravity_ads(framework, format)` — step-by-step guide for integrating ads into a publisher's app.

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

Restart Cursor or reload MCP servers. The 3 tools will appear in the tool list.

## Testing

```bash
cd mcp-server

# Unit tests (no server needed)
uv run pytest tests/ -v

# Smoke tests (server must be running)
uv run python server.py &
uv run python tests/smoke_test.py
```
