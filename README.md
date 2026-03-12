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

## Add to your AI editor

### Prerequisites

1. Clone the repo and install dependencies:

```bash
git clone https://github.com/trygravity/gravity-mcp.git
cd gravity-mcp/mcp-server
uv sync
```

2. Note the absolute paths you'll need:

```bash
which uv          # e.g. /Users/you/.local/bin/uv
pwd                # e.g. /Users/you/gravity-mcp/mcp-server
```

---

### Cursor

Open Cursor **Settings → MCP** and click **+ Add new MCP server**, or edit the JSON config file directly.

#### Option A: Remote (quickest — no local setup)

Add to `~/.cursor/mcp.json` (global) or `<project>/.cursor/mcp.json` (project-scoped):

```json
{
  "mcpServers": {
    "gravity": {
      "url": "https://gravity-mcp-server-production-8e67.up.railway.app/sse"
    }
  }
}
```

No cloning, no dependencies — just add the URL and restart Cursor.

#### Option B: stdio (local)

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "command": "/absolute/path/to/uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/gravity-mcp/mcp-server",
        "python", "server.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://gravity:gravity@localhost:5432/gravity",
        "GRAVITY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Replace the two `/absolute/path/to/...` values with the real paths from the prerequisite step. Get your API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). Requires `docker compose up db -d` for the local Postgres.

#### Option C: SSE (local Docker)

Start the server first:

```bash
docker compose up --build -d
```

Then add to your `mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Restart Cursor after editing the config. The Gravity tools will appear in the MCP panel.

---

### Claude Code

#### Option A: Remote (quickest — no local setup)

```bash
claude mcp add gravity --transport sse \
  --url https://gravity-mcp-server-production-8e67.up.railway.app/sse
```

#### Option B: CLI (local)

```bash
claude mcp add gravity \
  -- /absolute/path/to/uv run \
  --directory /absolute/path/to/gravity-mcp/mcp-server \
  python server.py
```

This writes the config to `~/.claude.json` automatically. To scope it to a single project, add the `-s project` flag.

#### Option C: JSON config (local)

Add to `~/.claude.json` (global) or `<project>/.mcp.json` (project-scoped):

```json
{
  "mcpServers": {
    "gravity": {
      "command": "/absolute/path/to/uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/gravity-mcp/mcp-server",
        "python", "server.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://gravity:gravity@localhost:5432/gravity",
        "GRAVITY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Other MCP clients

Any client that supports SSE transport can connect to the hosted server:

```
https://gravity-mcp-server-production-8e67.up.railway.app/sse
```

If your client only supports stdio, use `mcp-remote` as a bridge:

```bash
npx -y mcp-remote https://gravity-mcp-server-production-8e67.up.railway.app/sse
```

---

### Verify it works

Once connected, ask your AI assistant:

> "Search for Gravity ad formats in the card category"

You should see the `search_formats` tool get invoked and return matching ad formats.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRAVITY_API_KEY` | _(empty)_ | Publisher API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). Required for ad serving. Can also be passed via `Authorization: Bearer <key>` header on SSE/HTTP connections. |
| `LOG_LEVEL` | `INFO` | Python log level (DEBUG, INFO, WARNING, ERROR) |
| `DATABASE_URL` | _(empty)_ | PostgreSQL connection string. Auto-injected by Railway in production. For local dev: `postgresql://gravity:gravity@localhost:5432/gravity` |
| `PORT` | `8000` | HTTP server port. Auto-injected by Railway in production. |

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

## Project structure

```
mcp-server/
  server.py                     # FastMCP entrypoint (v0.2.0)
  tools/
    search_formats.py           # Format discovery tool
    build_theme.py              # Theme matching from design tokens
    generate_code.py            # Code generation + PostgreSQL registry
    troubleshoot.py             # Symptom-based diagnostics
  resources/
    format_catalog.py           # 25 ad format definitions
    docs.py                     # SDK documentation resources
  data/
    auth.py                     # API key extraction, validation, and hashing
    db.py                       # PostgreSQL persistence layer
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
