# Test Gate 1 — Scaffold + Docker Skeleton

## Context

Commit 1 created the bare project structure: `mcp-server/` with `pyproject.toml`, a minimal `server.py` (FastMCP + `/health` endpoint), empty subpackages, `Dockerfile`, `.dockerignore`, and `docker-compose.yml`. No tools or data yet — just the bootable skeleton.

## What to verify

1. `uv sync` installs dependencies without errors
2. The server starts and responds to `/health` with `"OK"`
3. The Docker image builds and the container passes its healthcheck

## Steps

### 1. Native server test

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv sync
```

**Expected:** No errors. A `uv.lock` file is created/updated and `.venv/` is populated.

```bash
uv run python server.py &
sleep 3
curl -f http://localhost:8000/health
```

**Expected output:** `OK`

```bash
kill %1
```

### 2. Docker build + healthcheck

```bash
cd /Users/worktrial/Desktop/gravity-mcp
docker compose up --build -d
sleep 10
docker compose ps
```

**Expected:** The `gravity-mcp` service shows status `healthy` (or `Up` with health: healthy).

```bash
curl -f http://localhost:8000/health
```

**Expected output:** `OK`

```bash
docker compose down
```

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `uv: command not found` | uv not in PATH | Run `export PATH="$HOME/.local/bin:$PATH"` or add to `~/.zshrc` |
| `uv sync` fails with resolver error | Bad `pyproject.toml` or `fastmcp` version | Check `pyproject.toml` has `fastmcp>=3.0` and `requires-python = ">=3.11"` |
| Server starts but `/health` returns 404 | `@mcp.custom_route` not wired | Check `server.py` has the `/health` route decorator |
| Docker build fails at `uv sync --frozen` | Missing `uv.lock` in build context | Run `uv lock` locally first, ensure `uv.lock` is not in `.dockerignore` |
| Container starts but healthcheck fails | `curl` not installed in runtime image | Check Dockerfile installs `curl` in the runtime stage |

## Pass criteria

All three checks pass:
- [ ] `uv sync` succeeds
- [ ] `curl http://localhost:8000/health` returns `OK` (native)
- [ ] `docker compose ps` shows healthy + `curl` returns `OK` (container)
