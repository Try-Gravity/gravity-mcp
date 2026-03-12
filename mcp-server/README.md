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
docker compose up --build -d

# Verify
curl http://localhost:8000/health    # → OK
curl http://localhost:8000/version   # → {"version":"0.2.0"}
docker compose logs -f               # watch logs
docker compose down                  # stop
```

This starts the MCP server and a PostgreSQL database. Placement records are persisted to the `pgdata` volume across container restarts.

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

## Connect from Cursor

### Option A: Remote (recommended for most users)

Point Cursor at the hosted server — no local setup required.

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "url": "https://gravity-mcp-server-production-8e67.up.railway.app/sse"
    }
  }
}
```

Restart Cursor to pick up changes. The remote server handles database persistence automatically.

### Option B: Local (stdio)

Run the server locally with full control over the environment.

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/gravity-mcp/mcp-server", "python", "server.py"],
      "env": {
        "DATABASE_URL": "postgresql://gravity:gravity@localhost:5432/gravity",
        "GRAVITY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Replace paths with your local values (`which uv` for the command). Get your API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). The `DATABASE_URL` env var requires the Docker Postgres to be running (`docker compose up db -d`). Restart Cursor to pick up changes.

### Option C: Remote via `npx`

If your MCP client doesn't support `url` connections directly, use the SSE transport proxy:

```json
{
  "mcpServers": {
    "gravity": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://gravity-mcp-server-production-8e67.up.railway.app/sse"]
    }
  }
}
```

## Testing

```bash
cd mcp-server

# Unit tests (no server needed, DB writes are mocked)
uv run pytest tests/test_tools.py -v

# Smoke tests (requires docker compose up -d)
uv run python tests/smoke_test.py
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRAVITY_API_KEY` | _(empty)_ | Publisher API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). Required for ad serving. Can also be passed via `Authorization: Bearer <key>` header on SSE/HTTP connections. |
| `LOG_LEVEL` | `INFO` | Python log level (DEBUG, INFO, WARNING, ERROR) |
| `DATABASE_URL` | _(empty)_ | PostgreSQL connection string. Auto-injected by Railway. For local dev: `postgresql://gravity:gravity@localhost:5432/gravity` |
| `PORT` | `8000` | HTTP server port. Auto-injected by Railway. |

## Production deployment

The server is deployed on Railway at:

```
https://gravity-mcp-server-production-8e67.up.railway.app
```

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check — returns `OK` |
| `/version` | Returns `{"version": "0.2.0"}` |
| `/sse` | SSE transport for MCP clients |

### Deploy your own instance

1. Push this repo to GitHub
2. Create a new Railway project from the repo
3. Set **Root Directory** to `mcp-server`
4. Add a **PostgreSQL** service — Railway auto-injects `DATABASE_URL`
5. Deploy — the `placements` table is auto-created on first request
6. Your MCP endpoint is `https://<app>.up.railway.app/sse`

### Redeploy from CLI

```bash
cd mcp-server
railway up --ci
```
