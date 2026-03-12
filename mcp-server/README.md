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
uv run python server.py http       # Streamable HTTP on port 8000 (for remote clients)
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
      "url": "https://gravity-mcp-server-production-8e67.up.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer your-api-key-here"
      }
    }
  }
}
```

Get your API key from [trygravity.ai/dashboard](https://trygravity.ai/dashboard). Restart Cursor to pick up changes. The remote server handles database persistence automatically.

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
      "args": [
        "-y", "mcp-remote",
        "https://gravity-mcp-server-production-8e67.up.railway.app/mcp",
        "--header",
        "Authorization:${GRAVITY_API_KEY}"
      ],
      "env": {
        "GRAVITY_API_KEY": "Bearer your-api-key-here"
      }
    }
  }
}
```

## Usage guide

Once the MCP server is connected, you can ask your AI assistant (Cursor, Claude, etc.) natural-language questions. Below are example queries grouped by task, with the expected behavior for each.

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
