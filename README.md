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

## Resources

| URI | Content |
|-----|---------|
| `gravity://formats` | Index of all 25 ad format names and descriptions |
| `gravity://formats/{name}` | Full detail for one format (code, type, omits) |
| `gravity://docs/{topic}` | SDK documentation by topic |

Doc topics: `ad-response`, `styling`, `react-component`, `server-sdk`, `js-sdk`, `placement-policy`, `checklist`

## Prompt

`integrate_gravity_ads(framework, format)` — step-by-step guide for integrating ads into a publisher's app. Automatically instructs the LLM to extract site theme tokens before generating code.

## Quick start

### Native (stdio — for Cursor)

```bash
cd mcp-server
uv sync
uv run python server.py          # stdio transport (default)
```

### Native (HTTP — for remote clients)

```bash
uv run python server.py http     # Streamable HTTP on port 8000
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
      "url": "https://gravity-mcp-server-production-8e67.up.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer your-api-key-here"
      }
    }
  }
}
```

Get your API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). No cloning, no dependencies — just add the URL and restart Cursor.

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

#### Option C: HTTP (local Docker)

Start the server first:

```bash
docker compose up --build -d
```

Then add to your `mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Restart Cursor after editing the config. The Gravity tools will appear in the MCP panel.

---

### Claude Code

#### Option A: Remote (quickest — no local setup)

```bash
claude mcp add gravity \
  --transport http \
  https://gravity-mcp-server-production-8e67.up.railway.app/mcp \
  --header "Authorization:Bearer your-api-key-here"
```

Get your API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). No cloning, no dependencies — just run the command and start a new conversation.

By default this saves to your local project config. To scope it globally (all projects), add `-s user`:

```bash
claude mcp add gravity -s user \
  --transport http \
  https://gravity-mcp-server-production-8e67.up.railway.app/mcp \
  --header "Authorization:Bearer your-api-key-here"
```

#### Option B: CLI (local stdio)

```bash
claude mcp add gravity \
  -e GRAVITY_API_KEY=your-api-key-here \
  -e DATABASE_URL=postgresql://gravity:gravity@localhost:5432/gravity \
  -- /absolute/path/to/uv run \
  --directory /absolute/path/to/gravity-mcp/mcp-server \
  python server.py
```

Replace the two `/absolute/path/to/...` values with the real paths from the prerequisite step. Get your API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). Requires `docker compose up db -d` for the local Postgres.

Add `-s project` to scope the config to the current project only.

#### Option C: Local Docker (HTTP)

Start the server first:

```bash
docker compose up --build -d
```

Then add it to Claude Code:

```bash
claude mcp add gravity \
  --transport http \
  http://localhost:8000/mcp
```

#### Option D: JSON config (manual)

You can also edit the config files directly instead of using the CLI.

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

#### Managing the server

```bash
claude mcp list              # see all configured MCP servers
claude mcp get gravity       # check the Gravity server config
claude mcp remove gravity    # remove the Gravity server
```

### Other MCP clients

Any client that supports streamable HTTP transport can connect to the hosted server:

```
https://gravity-mcp-server-production-8e67.up.railway.app/mcp
```

If your client only supports stdio, use `mcp-remote` as a bridge:

```bash
npx -y mcp-remote https://gravity-mcp-server-production-8e67.up.railway.app/mcp
```

---

### Verify it works

Once connected, ask your AI assistant:

> "Search for Gravity ad formats in the card category"

You should see the `search_formats` tool get invoked and return matching ad formats.

## Usage guide

Once the MCP server is connected, you can ask your AI assistant natural-language questions. Below are example queries grouped by task, with the expected behavior for each.

### Discovering ad formats

| Example query | Expected behavior |
|---|---|
| "What ad formats are available?" | Calls `search_formats(detail="summary")` → returns all 25 formats with name, description, and type |
| "Show me banner-style formats" | Calls `search_formats(category="banner")` → returns formats in the banner category |
| "Do you have a floating ad?" | Calls `search_formats(query="floating")` → returns matching format(s) |
| "Show me the full code for the card format" | Calls `search_formats(query="card", detail="full")` → returns format detail including JSX code |

### Previewing theme styles

| Example query | Expected behavior |
|---|---|
| "Preview a dark theme for the ad" | Calls `build_theme(bg_color="#18181B")` → returns resolved style + slotProps for a dark background |
| "My site uses bg #1a1a2e, accent #E11D48, and 16px border radius" | Calls `build_theme(bg_color="#1a1a2e", accent_color="#E11D48", border_radius=16)` → returns theme with those tokens applied |
| "What would the ad look like with Inter font and rounded corners?" | Calls `build_theme(font_family="Inter, sans-serif", border_radius=12)` → returns style preview |

### Generating integration code

| Example query | Expected behavior |
|---|---|
| "Generate a card ad for my FastAPI app with streaming" | Extracts site theme tokens first (reads your codebase), confirms placement, then calls `generate_code(format="card", framework="fastapi", streaming=True, ...)` → returns paired server + client code |
| "Add a banner ad to my Next.js app, below the response" | Same flow: extract theme → confirm placement → calls `generate_code(format="banner", framework="nextjs", placement="below_response", ...)` |
| "Regenerate the code with a dark theme" | Calls `generate_code(..., theme="dark")` → returns code with dark palette baked in |
| "Use my brand color #E11D48 for the CTA button" | Calls `generate_code(..., accent_color="#E11D48")` → returns code with custom accent |

**Expected multi-step flow:** The LLM should (1) scan your codebase for design tokens, (2) ask you to confirm ad placement and placement_id, (3) generate code with theme tokens passed in. If it skips theme extraction, ask it to check your Tailwind config or CSS variables first.

### Troubleshooting

| Example query | Expected behavior |
|---|---|
| "No ads are showing up" | Calls `troubleshoot(symptom="no ads showing")` → returns diagnosis: likely missing `GRAVITY_API_KEY`, with fix steps |
| "I'm getting a 401 error" | Calls `troubleshoot(symptom="401")` → returns: invalid/revoked API key, with regeneration instructions |
| "CORS error when fetching ads" | Calls `troubleshoot(symptom="CORS error")` → returns: ad fetch must be server-side, not client-side |
| "Impressions aren't tracking" | Calls `troubleshoot(symptom="impressions not counting")` → returns: `impUrl` not being fired, with fix code |
| "Only getting test ads, no revenue" | Calls `troubleshoot(symptom="test ads only")` → returns: `production: true` not set |
| "Ad request is timing out" | Calls `troubleshoot(symptom="timeout")` → returns: increase `timeoutMs`, start request early |
| "Clicks aren't being tracked" | Calls `troubleshoot(symptom="clicks don't track")` → returns: use `ad.clickUrl` not `ad.url` |

### Reading documentation

| Example query | Expected behavior |
|---|---|
| "What fields are in the ad response?" | Reads `gravity://docs/ad-response` → shows the `Ad` interface with all fields explained |
| "How do I style the ad component?" | Reads `gravity://docs/styling` → shows `style`, `slotProps`, and `className` methods with recipes |
| "Show me the integration checklist" | Reads `gravity://docs/checklist` → shows server-side and client-side verification items |
| "What placements are allowed?" | Reads `gravity://docs/placement-policy` → shows all valid placement values and rules |
| "How do I use the Python server SDK?" | Reads `gravity://docs/server-sdk` → shows `Gravity` class API and usage examples |
| "How do I send gravity context from the client?" | Reads `gravity://docs/js-sdk` → shows `gravityContext()` usage |

### End-to-end integration (using the prompt)

Asking "Help me integrate Gravity ads into my app" triggers the `integrate_gravity_ads` prompt, which walks through the full flow:

1. **Extract site theme** — LLM reads your Tailwind config, CSS variables, or component styles
2. **Discover formats** — shows available ad formats for you to pick
3. **Confirm placement** — asks where you want the ad and what tracking ID to use
4. **Generate code** — produces server + client code with your theme baked in
5. **Verify visual fit** — checks contrast, colors, and border radius match your site
6. **Verify integration** — walks through the checklist (API key, server-side fetch, impUrl, clickUrl, etc.)
7. **Troubleshoot** — diagnoses any issues you report

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
uv run python server.py http &
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
| `/mcp` | Streamable HTTP transport for MCP clients |

### Deploy your own instance

1. Push this repo to GitHub
2. Create a new Railway project from the repo
3. Set **Root Directory** to `mcp-server`
4. Add a **PostgreSQL** service — Railway auto-injects `DATABASE_URL`
5. Deploy — the `placements` table is auto-created on first request
6. Your MCP endpoint is `https://<app>.up.railway.app/mcp`

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
