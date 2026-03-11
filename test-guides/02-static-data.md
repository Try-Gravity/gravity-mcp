# Test Gate 2 — Static Data Modules

## Context

Commit 2 added three static data modules that tools will consume:
- `mcp-server/resources/format_catalog.py` — `FORMAT_CATALOG` dict with 25 ad format entries
- `mcp-server/data/style_type_map.py` — `STYLE_TYPE_MAP` dict mapping 25 style names to SDK variants
- `mcp-server/data/troubleshoot_kb.py` — `TROUBLESHOOT_KB` list with 10 symptom/cause/fix entries

No tools are registered yet. The server still only has `/health`.

## What to verify

1. All three modules import without errors
2. Correct entry counts (25 formats, 25 styles, 10 KB entries)
3. Keys are consistent between `FORMAT_CATALOG` and `STYLE_TYPE_MAP`
4. Each KB entry has the required fields
5. Each format entry has the required fields

## Steps

### 1. Import and count assertions

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from resources.format_catalog import FORMAT_CATALOG
from data.style_type_map import STYLE_TYPE_MAP
from data.troubleshoot_kb import TROUBLESHOOT_KB

# Count checks
assert len(FORMAT_CATALOG) == 25, f'Expected 25 formats, got {len(FORMAT_CATALOG)}'
assert len(STYLE_TYPE_MAP) == 25, f'Expected 25 styles, got {len(STYLE_TYPE_MAP)}'
assert len(TROUBLESHOOT_KB) == 10, f'Expected 10 KB entries, got {len(TROUBLESHOOT_KB)}'
print(f'Counts OK: {len(FORMAT_CATALOG)} formats, {len(STYLE_TYPE_MAP)} styles, {len(TROUBLESHOOT_KB)} KB entries')
"
```

**Expected:** `Counts OK: 25 formats, 25 styles, 10 KB entries`

### 2. Key consistency check

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from resources.format_catalog import FORMAT_CATALOG
from data.style_type_map import STYLE_TYPE_MAP

catalog_keys = set(FORMAT_CATALOG.keys())
style_keys = set(STYLE_TYPE_MAP.keys())
missing_in_styles = catalog_keys - style_keys
missing_in_catalog = style_keys - catalog_keys
assert not missing_in_styles, f'In catalog but not style map: {missing_in_styles}'
assert not missing_in_catalog, f'In style map but not catalog: {missing_in_catalog}'
print('Key consistency OK — catalog and style map have identical keys')
"
```

**Expected:** `Key consistency OK — catalog and style map have identical keys`

### 3. Schema validation

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from resources.format_catalog import FORMAT_CATALOG
from data.troubleshoot_kb import TROUBLESHOOT_KB

# Format entry schema
required_format_fields = {'name', 'description', 'type', 'code', 'omits'}
for key, entry in FORMAT_CATALOG.items():
    missing = required_format_fields - set(entry.keys())
    assert not missing, f'Format \"{key}\" missing fields: {missing}'
print(f'All {len(FORMAT_CATALOG)} format entries have required fields')

# KB entry schema
required_kb_fields = {'keywords', 'symptom', 'cause', 'fix', 'reference_url'}
for i, entry in enumerate(TROUBLESHOOT_KB):
    missing = required_kb_fields - set(entry.keys())
    assert not missing, f'KB entry {i} missing fields: {missing}'
print(f'All {len(TROUBLESHOOT_KB)} KB entries have required fields')
"
```

**Expected:**
```
All 25 format entries have required fields
All 10 KB entries have required fields
```

### 4. Spot check — verify specific entries exist

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from resources.format_catalog import FORMAT_CATALOG
from data.style_type_map import STYLE_TYPE_MAP

# Spot-check known formats
assert 'card' in FORMAT_CATALOG, 'Missing card format'
assert 'floating' in FORMAT_CATALOG, 'Missing floating format'
assert 'banner' in FORMAT_CATALOG, 'Missing banner format'
assert 'notification' in FORMAT_CATALOG, 'Missing notification format'
assert 'hyperlink' in FORMAT_CATALOG, 'Missing hyperlink format'

# Spot-check type mappings
assert STYLE_TYPE_MAP['floating'] == 'card', f'floating should map to card, got {STYLE_TYPE_MAP[\"floating\"]}'
assert STYLE_TYPE_MAP['compact-bar'] == 'inline', f'compact-bar should map to inline'
assert STYLE_TYPE_MAP['banner'] == 'banner', f'banner should map to banner'

# Verify format code is non-empty
for key, entry in FORMAT_CATALOG.items():
    assert len(entry['code'].strip()) > 20, f'Format \"{key}\" has suspiciously short code'

print('Spot checks OK')
"
```

**Expected:** `Spot checks OK`

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError` | Missing `__init__.py` in `resources/` or `data/` | Ensure both dirs have `__init__.py` |
| Count mismatch | Missing or extra entries | Cross-reference with the 25 format names in PLAN.md section 4 |
| Key mismatch | Typo in a format name | Diff the keys between both dicts — fix the typo |
| Missing field | Incomplete entry | Add the missing field to the specific entry |

## Pass criteria

- [ ] All 3 modules import cleanly
- [ ] 25 formats, 25 styles, 10 KB entries
- [ ] Catalog and style map keys match exactly
- [ ] All entries have required fields
- [ ] Spot checks pass (known formats exist, type mappings correct, code non-empty)
