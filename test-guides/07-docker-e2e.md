# Test Gate 7 — README + Docker E2E + Cursor Config

## Context

Commit 7 added:
- `mcp-server/README.md` — full setup, run, Docker, test, and Cursor config instructions
- Final verification that the Docker image includes all code from commits 1-6

This is the final commit. Everything should work end-to-end in Docker and be ready for Cursor integration.

## What to verify

1. Docker image builds successfully with all layers
2. Container passes healthcheck
3. All 3 tools work inside the container via smoke tests
4. Resources are accessible from the container
5. CSV persistence works via volume mount
6. README exists and has required sections
7. (Manual) Cursor discovers the server and tools

## Steps

### 1. Clean Docker build

```bash
cd /Users/worktrial/Desktop/gravity-mcp

# Remove any stale containers/images
docker compose down --rmi local 2>/dev/null

# Build fresh
docker compose up --build -d
```

**Expected:** Build completes without errors. Watch for:
- `uv sync --frozen` succeeds (deps installed)
- All COPY layers succeed (no missing files)
- Container starts

### 2. Healthcheck

```bash
# Wait for container to be healthy
sleep 10
docker compose ps
```

**Expected:** Service shows `healthy` status.

```bash
curl -f http://localhost:8000/health
```

**Expected:** `OK`

### 3. Full smoke test against container

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server

# Clean up any local CSV to prove the container creates its own
rm -f data/placements.csv

uv run python tests/smoke_test.py
```

**Expected:** All 12 steps PASS, ending with `--- ALL SMOKE TESTS PASSED ---`.

### 4. CSV persistence via volume mount

```bash
# Check CSV was created in the mounted volume
ls -la /Users/worktrial/Desktop/gravity-mcp/mcp-server/data/placements.csv
cat /Users/worktrial/Desktop/gravity-mcp/mcp-server/data/placements.csv
```

**Expected:** CSV file exists with header + at least 2 data rows from the smoke test's `generate_code` calls.

```bash
# Restart container — CSV should survive
docker compose restart
sleep 10
docker compose ps  # still healthy

# Verify CSV persisted
wc -l /Users/worktrial/Desktop/gravity-mcp/mcp-server/data/placements.csv
```

**Expected:** Same row count as before restart (CSV not wiped).

### 5. Docker layer caching verification

```bash
cd /Users/worktrial/Desktop/gravity-mcp

# Make a trivial change to server.py (e.g., touch it)
touch mcp-server/server.py

# Rebuild — should only rebuild layer 3 (application code)
docker compose up --build -d 2>&1 | tail -20
```

**Expected:** You should see `CACHED` for the dependency install layer and the data/templates layer. Only the final COPY (tools + server.py) rebuilds.

### 6. README validation

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
cat README.md | head -5
```

**Expected:** README exists and has a title.

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
content = open('README.md').read()
required = ['uv sync', 'server.py', 'docker', '8000', 'mcp.json', 'pytest', 'smoke']
missing = [r for r in required if r.lower() not in content.lower()]
assert not missing, f'README missing sections about: {missing}'
print(f'PASS: README contains all {len(required)} required topics')
"
```

**Expected:** `PASS: README contains all 7 required topics`

### 7. Clean up

```bash
docker compose down
```

### 8. (Manual) Cursor E2E — publisher simulation

This step is done manually in Cursor. Start the server first:

```bash
cd /Users/worktrial/Desktop/gravity-mcp
docker compose up -d
```

Then add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gravity": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Restart Cursor (or reload MCP servers from the command palette).

**Test prompt 1** — format discovery:
> "I want to integrate Gravity ads into my app. Show me what ad formats are available."

Expected: Cursor calls `search_formats` and lists formats.

**Test prompt 2** — code generation:
> "I want a floating card with dark mode. My backend is Next.js with streaming."

Expected: Cursor calls `generate_code(format="floating", framework="nextjs", streaming=True, theme="dark")` and returns paired server + client code.

**Test prompt 3** — troubleshooting:
> "My ads aren't showing, I'm getting an empty array."

Expected: Cursor calls `troubleshoot` and returns the API key diagnosis.

**Checklist:**
- [ ] Cursor discovers the 3 tools on server connect
- [ ] `search_formats` returns correct format list
- [ ] `generate_code` returns code with correct imports
- [ ] Generated code includes `gravityContext()` on client side
- [ ] Generated code includes `production: true` comment
- [ ] `placement_id` appears in both return value and CSV
- [ ] `troubleshoot` returns relevant diagnosis
- [ ] Resources readable (ask: "show me the Ad response interface")

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Docker build fails at COPY | File not in build context or in `.dockerignore` | Check `.dockerignore` doesn't exclude needed files |
| Container unhealthy | Server crashes on startup | Run `docker compose logs gravity-mcp` to see error |
| Smoke test fails against container | Port not mapped or server not ready | Increase sleep time, check `docker compose ps` |
| CSV not persisted | Volume mount wrong | Check `docker-compose.yml` mounts `./mcp-server/data:/app/data` |
| Layer caching not working | `.dockerignore` missing, sending full context | Ensure `.dockerignore` excludes `.git`, `__pycache__`, `.venv` |
| Cursor doesn't find tools | Wrong MCP URL or server not running | Verify `http://localhost:8000/mcp` is accessible, restart Cursor |

## Pass criteria

- [ ] Docker image builds cleanly
- [ ] Container healthcheck passes
- [ ] All 12 smoke test steps pass against container
- [ ] CSV persists across container restart (volume mount works)
- [ ] Layer caching works (only changed layers rebuild)
- [ ] README has all required sections
- [ ] (Manual) Cursor E2E prompts work
