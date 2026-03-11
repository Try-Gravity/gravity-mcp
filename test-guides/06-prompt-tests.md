# Test Gate 6 — Prompt Template + Full Test Suite

## Context

Commit 6 added:
- `integrate_gravity_ads` prompt template registered in `server.py`
- `mcp-server/tests/test_tools.py` — full pytest suite (~17 tests across all 3 tools)
- `mcp-server/tests/smoke_test.py` — 12-step integration test via FastMCP Client over HTTP
- `pytest` added to dev dependencies in `pyproject.toml`

## What to verify

1. `uv sync --dev` installs pytest
2. All unit tests pass via `pytest`
3. Smoke tests pass against the running server (all 3 tools + resources + CSV)
4. Prompt template is registered and retrievable

## Steps

### 1. Install dev dependencies

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv sync --dev
uv run pytest --version
```

**Expected:** pytest version prints (e.g., `pytest 8.x.x`).

### 2. Run full unit test suite

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
rm -f data/placements.csv
uv run pytest tests/test_tools.py -v
```

**Expected:** All tests pass. Look for output like:

```
tests/test_tools.py::test_names_returns_25 PASSED
tests/test_tools.py::test_summary_has_required_fields PASSED
tests/test_tools.py::test_full_has_code PASSED
tests/test_tools.py::test_filter_by_category PASSED
tests/test_tools.py::test_filter_by_query PASSED
tests/test_tools.py::test_empty_results PASSED
tests/test_tools.py::test_returns_paired_code PASSED
tests/test_tools.py::test_placement_id_is_uuid PASSED
tests/test_tools.py::test_csv_write PASSED
tests/test_tools.py::test_placement_id_in_server_code PASSED
tests/test_tools.py::test_unknown_format_rejected PASSED
tests/test_tools.py::test_dark_theme_includes_dark_styles PASSED
tests/test_tools.py::test_all_framework_streaming_combos PASSED
tests/test_tools.py::test_known_symptom_match PASSED
tests/test_tools.py::test_case_insensitive PASSED
tests/test_tools.py::test_unknown_symptom_fallback PASSED
tests/test_tools.py::test_all_entries_reachable PASSED
```

If any test fails, read the failure output and fix the issue before proceeding.

### 3. Run smoke tests against running server

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
rm -f data/placements.csv
uv run python server.py &
SERVER_PID=$!
sleep 3

# Verify server is up
curl -sf http://localhost:8000/health && echo " — server healthy"

# Run the full smoke test
uv run python tests/smoke_test.py

kill $SERVER_PID 2>/dev/null
```

**Expected:** Each of the 12 smoke test steps prints `PASS`, ending with `--- ALL SMOKE TESTS PASSED ---`.

The 12 steps are:
1. `search_formats` — names mode
2. `search_formats` — query filter
3. `search_formats` — full mode with code
4. `generate_code` — nextjs streaming
5. `generate_code` — dark theme
6. `generate_code` — unknown format rejected
7. `troubleshoot` — known symptom
8. `troubleshoot` — unknown symptom fallback
9. Resource — `gravity://formats` index
10. Resource — `gravity://formats/banner` detail
11. Resource — `gravity://docs/ad-response` topic
12. CSV verification — at least 2 rows from generate_code calls

### 4. Prompt template verification

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python server.py &
SERVER_PID=$!
sleep 3

uv run python -c "
import asyncio
from fastmcp import Client

async def test():
    client = Client('http://localhost:8000/mcp')
    async with client:
        # List prompts — integrate_gravity_ads should be present
        prompts = await client.list_prompts()
        prompt_names = [p.name for p in prompts]
        assert 'integrate_gravity_ads' in prompt_names, f'Prompt not found. Available: {prompt_names}'
        print(f'PASS: integrate_gravity_ads prompt registered. All prompts: {prompt_names}')

        # Get the prompt with arguments
        r = await client.get_prompt('integrate_gravity_ads', {
            'framework': 'nextjs',
            'format': 'floating',
        })
        text = str(r)
        assert len(text) > 100, f'Prompt response too short: {len(text)} chars'
        print(f'PASS: Prompt returns {len(text)} chars of guidance')

asyncio.run(test())
"

kill $SERVER_PID 2>/dev/null
```

**Expected:** Two PASS lines.

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `pytest: command not found` | pytest not in dev deps | Add `pytest` to `[project.optional-dependencies]` dev list and `uv sync --dev` |
| Unit test import error | Wrong import path in test file | Check test imports match actual module paths |
| Smoke test connection refused | Server not running or wrong port | Ensure server started successfully on port 8000 |
| Smoke test assertion fails | Tool behavior doesn't match expected output | Read the specific FAIL message, fix the tool, re-run |
| Prompt not found | Prompt not registered in `server.py` | Verify `@mcp.prompt()` decorator is used |
| CSV row count wrong | Prior runs left stale CSV | Delete `data/placements.csv` before testing |

## Pass criteria

- [ ] `uv sync --dev` installs pytest
- [ ] `uv run pytest tests/test_tools.py -v` — all tests pass (0 failures)
- [ ] `uv run python tests/smoke_test.py` — ALL SMOKE TESTS PASSED
- [ ] `integrate_gravity_ads` prompt is registered and returns content
