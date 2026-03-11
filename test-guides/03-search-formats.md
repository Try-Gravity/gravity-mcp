# Test Gate 3 — search_formats Tool + Resource Templates

## Context

Commit 3 added:
- `mcp-server/tools/search_formats.py` — the `search_formats` tool with `query`, `category`, and `detail` params
- `mcp-server/resources/docs.py` — resource templates for `gravity://formats`, `gravity://formats/{name}`, `gravity://docs/{topic}`
- Updated `mcp-server/server.py` to register the tool and resources

## What to verify

1. `search_formats` works as a plain Python function (unit level)
2. All three filter modes work: `names`, `summary`, `full`
3. Category filtering returns only matching types
4. Query filtering matches on name + description
5. Empty results return an empty list (not an error)
6. The server starts with the tool registered
7. Resource templates are accessible

## Steps

### 1. Unit test — detail levels

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.search_formats import search_formats

# names mode
r = search_formats(detail='names')
assert isinstance(r, list), f'Expected list, got {type(r)}'
assert len(r) == 25, f'Expected 25 names, got {len(r)}'
assert all(isinstance(name, str) for name in r), 'Names should be strings'
print(f'PASS: names mode returns {len(r)} strings')

# summary mode
r = search_formats(detail='summary')
assert len(r) == 25, f'Expected 25 summaries, got {len(r)}'
assert all('name' in e and 'description' in e and 'type' in e for e in r), 'Summary missing fields'
assert all('code' not in e for e in r), 'Summary should not include code'
print(f'PASS: summary mode returns {len(r)} dicts with name/description/type')

# full mode
r = search_formats(detail='full')
assert len(r) == 25, f'Expected 25 full entries, got {len(r)}'
assert all('code' in e and 'omits' in e for e in r), 'Full mode missing code or omits'
print(f'PASS: full mode returns {len(r)} dicts with code and omits')
"
```

**Expected:** Three PASS lines.

### 2. Unit test — category filter

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.search_formats import search_formats

# Filter by category 'card'
r = search_formats(category='card', detail='summary')
assert len(r) > 0, 'No card-type formats found'
assert all(e['type'] == 'card' for e in r), f'Non-card types in results: {[e[\"type\"] for e in r]}'
card_names = [e['name'] for e in r]
assert 'card' in card_names, 'card format not in card category'
assert 'floating' in card_names, 'floating format not in card category'
print(f'PASS: category=card returns {len(r)} entries: {card_names}')

# Filter by category 'banner'
r = search_formats(category='banner', detail='names')
assert len(r) >= 1, 'No banner-type formats found'
print(f'PASS: category=banner returns {len(r)} entries')

# Non-existent category returns empty
r = search_formats(category='nonexistent', detail='names')
assert r == [], f'Expected empty list for unknown category, got {r}'
print('PASS: unknown category returns empty list')
"
```

**Expected:** Three PASS lines.

### 3. Unit test — query filter

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.search_formats import search_formats

# Query by name
r = search_formats(query='float', detail='summary')
assert any('floating' in e['name'] for e in r), 'floating not found for query=float'
print(f'PASS: query=float finds floating ({len(r)} results)')

# Query by description keyword
r = search_formats(query='notification', detail='summary')
assert len(r) >= 1, 'No results for query=notification'
print(f'PASS: query=notification returns {len(r)} results')

# Combined query + category
r = search_formats(query='float', category='card', detail='names')
assert 'floating' in r, 'floating not found with query+category'
print(f'PASS: query=float + category=card returns {r}')

# No results query
r = search_formats(query='xyznonexistent', detail='names')
assert r == [], f'Expected empty for nonsense query, got {r}'
print('PASS: nonsense query returns empty list')
"
```

**Expected:** Four PASS lines.

### 4. Integration test — server starts with tool registered

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python server.py &
SERVER_PID=$!
sleep 3

# Verify server is up
curl -sf http://localhost:8000/health
echo ""

# Verify MCP endpoint exists (should return something, not 404)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/mcp)
echo "MCP endpoint returned HTTP $HTTP_CODE"

kill $SERVER_PID 2>/dev/null
```

**Expected:** `OK` on the first line, and the MCP endpoint does not return 404.

### 5. Resource template test (via FastMCP Client)

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
        # Format index
        r = await client.read_resource('gravity://formats')
        text = str(r)
        assert 'floating' in text, 'formats index missing floating'
        assert 'banner' in text, 'formats index missing banner'
        print('PASS: gravity://formats returns format index')

        # Single format detail
        r = await client.read_resource('gravity://formats/banner')
        text = str(r)
        assert 'banner' in text.lower(), 'format detail missing banner content'
        print('PASS: gravity://formats/banner returns detail')

        # Doc topic
        r = await client.read_resource('gravity://docs/checklist')
        text = str(r)
        assert len(text) > 50, 'checklist doc too short'
        print('PASS: gravity://docs/checklist returns content')

asyncio.run(test())
"

kill $SERVER_PID 2>/dev/null
```

**Expected:** Three PASS lines.

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ImportError: cannot import search_formats` | Function not exported or wrong module path | Check `tools/search_formats.py` defines the function and `tools/__init__.py` exists |
| Category filter returns wrong types | Filter comparing wrong field | Ensure filter checks entry `type` field, not `name` |
| Resources return 404 | Resource templates not registered in `server.py` | Verify `docs.py` resources are imported and registered |
| MCP Client can't connect | Server not running or wrong URL | Check server logs, ensure port 8000 is free |

## Pass criteria

- [ ] `detail="names"` returns 25 strings
- [ ] `detail="summary"` returns 25 dicts with name/description/type (no code)
- [ ] `detail="full"` returns 25 dicts with code and omits
- [ ] `category="card"` returns only card-type entries
- [ ] `query="float"` finds floating
- [ ] Empty results return `[]`, not an error
- [ ] Server starts with tool registered
- [ ] `gravity://formats`, `gravity://formats/{name}`, `gravity://docs/{topic}` resources are readable
