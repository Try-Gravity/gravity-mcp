# Test Gate 4 — Integration Templates + generate_code Tool

## Context

Commit 4 added:
- 7 server integration templates in `mcp-server/templates/` (nextjs/express/fastapi x streaming/nonstreaming + vanilla)
- `mcp-server/tools/generate_code.py` — the `generate_code` tool with UUID generation, template assembly, and CSV write
- Updated `mcp-server/server.py` to register the tool

## What to verify

1. All 7 templates import and contain non-empty code strings with `{placement_id}` slot
2. `generate_code` returns paired server + client code
3. `placement_id` is a valid UUID v4 embedded in server code
4. CSV row is written to `data/placements.csv` with correct fields
5. Unknown format is rejected with an error
6. Dark theme appends dark mode styles
7. All 6 framework/streaming combos produce output (+ vanilla)

## Steps

### 1. Template import validation

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from templates.nextjs_streaming import TEMPLATE as t1
from templates.nextjs_nonstreaming import TEMPLATE as t2
from templates.express_streaming import TEMPLATE as t3
from templates.express_nonstreaming import TEMPLATE as t4
from templates.fastapi_streaming import TEMPLATE as t5
from templates.fastapi_nonstreaming import TEMPLATE as t6
from templates.vanilla_client import TEMPLATE as t7

templates = [t1, t2, t3, t4, t5, t6, t7]
names = ['nextjs_streaming', 'nextjs_nonstreaming', 'express_streaming', 'express_nonstreaming',
         'fastapi_streaming', 'fastapi_nonstreaming', 'vanilla_client']

for name, tmpl in zip(names, templates):
    assert isinstance(tmpl, str), f'{name} is not a string'
    assert len(tmpl) > 100, f'{name} is suspiciously short ({len(tmpl)} chars)'
    assert '{placement_id}' in tmpl, f'{name} missing {{placement_id}} slot'
    print(f'PASS: {name} — {len(tmpl)} chars, has placement_id slot')

print(f'\\nAll {len(templates)} templates valid')
"
```

**Expected:** 7 PASS lines + summary.

### 2. Basic generate_code call

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
# Clean up any leftover CSV from prior runs
rm -f data/placements.csv

uv run python -c "
from tools.generate_code import generate_code
import uuid

r = generate_code(format='floating', framework='nextjs', streaming=True)

# Check required fields
assert 'placement_id' in r, f'Missing placement_id. Keys: {list(r.keys())}'
assert 'server_code' in r, 'Missing server_code'
assert 'client_code' in r, 'Missing client_code'
assert 'style' in r, 'Missing style'
assert 'type' in r, 'Missing type'
print(f'PASS: Result has all required fields')

# Validate UUID format
pid = r['placement_id']
parsed = uuid.UUID(pid, version=4)
assert str(parsed) == pid, f'placement_id is not valid UUID v4: {pid}'
print(f'PASS: placement_id is valid UUID v4: {pid}')

# Check placement_id appears in server code
assert pid in r['server_code'], 'placement_id not found in server_code'
print('PASS: placement_id embedded in server_code')

# Check metadata
assert r['style'] == 'floating', f'Expected style=floating, got {r[\"style\"]}'
assert r['type'] == 'card', f'Expected type=card, got {r[\"type\"]}'
assert r['framework'] == 'nextjs', f'Expected framework=nextjs, got {r[\"framework\"]}'
print(f'PASS: Metadata correct — style={r[\"style\"]}, type={r[\"type\"]}, framework={r[\"framework\"]}')
"
```

**Expected:** Four PASS lines.

### 3. CSV write verification

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
import csv
from pathlib import Path

csv_path = Path('data/placements.csv')
assert csv_path.exists(), 'placements.csv was not created'

with open(csv_path) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

assert len(rows) >= 1, f'Expected at least 1 row, got {len(rows)}'

row = rows[0]
required_cols = {'placement_id', 'style', 'type', 'framework', 'platform', 'performance', 'created_at'}
actual_cols = set(row.keys())
missing = required_cols - actual_cols
assert not missing, f'CSV missing columns: {missing}'
print(f'PASS: CSV has {len(rows)} rows with columns: {sorted(actual_cols)}')

assert row['style'] == 'floating', f'Expected style=floating, got {row[\"style\"]}'
assert row['platform'] == 'web', f'Expected platform=web, got {row[\"platform\"]}'
assert len(row['created_at']) > 10, f'created_at looks wrong: {row[\"created_at\"]}'
print(f'PASS: First row — style={row[\"style\"]}, platform={row[\"platform\"]}, created_at={row[\"created_at\"]}')
"
```

**Expected:** Two PASS lines.

### 4. Unknown format rejection

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.generate_code import generate_code

r = generate_code(format='nonexistent_format_xyz', framework='nextjs', streaming=True)
text = str(r).lower()
assert 'error' in text or 'unknown' in text or 'not found' in text, f'Expected error for unknown format, got: {r}'
print(f'PASS: Unknown format rejected — response contains error message')
"
```

**Expected:** One PASS line.

### 5. Dark theme test

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.generate_code import generate_code

r = generate_code(format='card', framework='express', streaming=False, theme='dark')
combined = r.get('client_code', '') + r.get('server_code', '')
lower = combined.lower()
assert 'dark' in lower or '#18181b' in lower or 'slotprops' in lower, f'Dark theme not reflected in output'
print('PASS: Dark theme includes dark mode styling')
"
```

**Expected:** One PASS line.

### 6. All framework/streaming combinations

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
rm -f data/placements.csv

uv run python -c "
from tools.generate_code import generate_code

combos = [
    ('nextjs', True), ('nextjs', False),
    ('express', True), ('express', False),
    ('fastapi', True), ('fastapi', False),
]

for framework, streaming in combos:
    r = generate_code(format='card', framework=framework, streaming=streaming)
    assert r.get('server_code'), f'{framework}/streaming={streaming}: missing server_code'
    assert r.get('client_code'), f'{framework}/streaming={streaming}: missing client_code'
    assert r.get('placement_id'), f'{framework}/streaming={streaming}: missing placement_id'
    print(f'PASS: {framework} streaming={streaming}')

# Vanilla
r = generate_code(format='card', framework='vanilla', streaming=False)
assert r.get('client_code') or r.get('server_code'), 'vanilla: missing code'
print('PASS: vanilla')

import csv
with open('data/placements.csv') as f:
    rows = list(csv.DictReader(f))
print(f'\\nAll 7 combos passed. CSV now has {len(rows)} rows.')
"
```

**Expected:** 7 PASS lines + row count summary.

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Template import fails | Wrong variable name or missing file | Ensure each template file exports `TEMPLATE` as a string |
| `{placement_id}` not in template | Template uses different slot name | Standardize on `{placement_id}` in all templates |
| CSV not created | `data/` directory missing or write path wrong | Ensure `data/` exists and `generate_code` writes relative to its own package |
| `fcntl` import error on non-Linux | macOS should work, Windows won't | `fcntl` works on macOS — check the import |
| UUID not in server_code | Template `.format()` not applying the slot | Verify template uses `{placement_id}` (not `{{placement_id}}` which escapes it) |

## Pass criteria

- [ ] All 7 templates import and have `{placement_id}` slot
- [ ] `generate_code` returns `placement_id`, `server_code`, `client_code`, `style`, `type`
- [ ] `placement_id` is valid UUID v4 and appears in `server_code`
- [ ] `data/placements.csv` is created with correct columns and values
- [ ] Unknown format returns an error message
- [ ] `theme="dark"` includes dark mode styling
- [ ] All 6 framework/streaming combos + vanilla produce output
