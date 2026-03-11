# Test Gate 5 — troubleshoot Tool

## Context

Commit 5 added:
- `mcp-server/tools/troubleshoot.py` — keyword-matching troubleshoot tool against the KB from Commit 2
- Updated `mcp-server/server.py` to register the tool

All 3 tools are now functional. The server is feature-complete.

## What to verify

1. Known symptoms match the correct KB entry
2. Matching is case-insensitive
3. Unknown symptoms return a fallback with common symptom list
4. Every KB entry is reachable by at least one of its keywords
5. All 3 tools are callable on the running server

## Steps

### 1. Known symptom matching

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.troubleshoot import troubleshoot

# Test each known symptom area
tests = [
    ('no ads', ['key', 'api', 'GRAVITY_API_KEY']),
    ('401', ['invalid', 'revoked', 'key']),
    ('test ads only', ['production']),
    ('impressions not tracking', ['impUrl', 'imp', 'intersection']),
    ('impression expired', ['5 minute', 'expired', 'time']),
    ('CORS', ['client', 'server-side', 'cors']),
    ('timeout', ['timeout', 'timeoutMs']),
    ('clickUrl', ['clickUrl', 'url']),
    ('gravityContext missing', ['gravity_context', 'context']),
    ('wrong placement', ['above_response', 'below_response', 'placement']),
]

passed = 0
for symptom, expected_any in tests:
    r = troubleshoot(symptom=symptom)
    text = str(r).lower()
    matched = any(kw.lower() in text for kw in expected_any)
    status = 'PASS' if matched else 'FAIL'
    if not matched:
        print(f'{status}: symptom=\"{symptom}\" — expected one of {expected_any} in response')
        print(f'  Got: {str(r)[:200]}')
    else:
        print(f'{status}: symptom=\"{symptom}\"')
        passed += 1

print(f'\\n{passed}/{len(tests)} known symptoms matched')
assert passed == len(tests), f'Not all symptoms matched'
"
```

**Expected:** 10 PASS lines, `10/10 known symptoms matched`.

### 2. Case-insensitive matching

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.troubleshoot import troubleshoot

r_lower = troubleshoot(symptom='no ads')
r_upper = troubleshoot(symptom='NO ADS')
r_mixed = troubleshoot(symptom='No Ads')

# All three should match the same entry
assert str(r_lower) == str(r_upper) == str(r_mixed), 'Case sensitivity detected'
print('PASS: Case-insensitive — no ads / NO ADS / No Ads all return same result')
"
```

**Expected:** One PASS line.

### 3. Unknown symptom fallback

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.troubleshoot import troubleshoot

r = troubleshoot(symptom='my cat walked on the keyboard')
text = str(r).lower()
has_fallback = 'contact' in text or 'support' in text or 'common' in text or 'known' in text
assert has_fallback, f'Fallback response missing contact/support/common indicator. Got: {text[:300]}'
print('PASS: Unknown symptom returns fallback response')

# Verify fallback lists some known symptoms
has_examples = any(kw in text for kw in ['no ads', '401', 'cors', 'timeout', 'impression'])
assert has_examples, f'Fallback should list common symptoms. Got: {text[:300]}'
print('PASS: Fallback includes common symptom examples')
"
```

**Expected:** Two PASS lines.

### 4. KB coverage — every entry reachable

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
uv run python -c "
from tools.troubleshoot import troubleshoot
from data.troubleshoot_kb import TROUBLESHOOT_KB

unreachable = []
for i, entry in enumerate(TROUBLESHOOT_KB):
    # Try each keyword for this entry
    reached = False
    for keyword in entry['keywords']:
        r = troubleshoot(symptom=keyword)
        if entry['cause'].lower() in str(r).lower() or entry['symptom'].lower() in str(r).lower():
            reached = True
            break
    if not reached:
        unreachable.append((i, entry['symptom'], entry['keywords']))

if unreachable:
    for idx, symptom, keywords in unreachable:
        print(f'FAIL: KB entry {idx} (\"{symptom}\") not reachable via keywords {keywords}')
    assert False, f'{len(unreachable)} KB entries unreachable'
else:
    print(f'PASS: All {len(TROUBLESHOOT_KB)} KB entries reachable by their keywords')
"
```

**Expected:** One PASS line.

### 5. All 3 tools callable on running server

```bash
cd /Users/worktrial/Desktop/gravity-mcp/mcp-server
rm -f data/placements.csv
uv run python server.py &
SERVER_PID=$!
sleep 3

uv run python -c "
import asyncio
from fastmcp import Client

async def test():
    client = Client('http://localhost:8000/mcp')
    async with client:
        # Tool 1: search_formats
        r = await client.call_tool('search_formats', {'detail': 'names'})
        assert 'card' in str(r), 'search_formats failed'
        print('PASS: search_formats callable')

        # Tool 2: generate_code
        r = await client.call_tool('generate_code', {
            'format': 'card',
            'framework': 'nextjs',
            'streaming': True,
        })
        assert 'placement_id' in str(r) or 'server_code' in str(r), 'generate_code failed'
        print('PASS: generate_code callable')

        # Tool 3: troubleshoot
        r = await client.call_tool('troubleshoot', {'symptom': 'no ads'})
        assert 'key' in str(r).lower() or 'api' in str(r), 'troubleshoot failed'
        print('PASS: troubleshoot callable')

        print('\\nAll 3 tools callable via MCP protocol')

asyncio.run(test())
"

kill $SERVER_PID 2>/dev/null
```

**Expected:** Three PASS lines + summary.

## Diagnosing failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Known symptom doesn't match | Keyword not in the `keywords` list for that KB entry | Add the keyword to the entry's `keywords` array |
| Case sensitivity | Matching not lowercasing both sides | Ensure `symptom.lower()` compared against `keyword.lower()` |
| Fallback missing symptom list | Fallback logic doesn't include examples | Return top 5 `symptom` fields from KB in the fallback |
| KB entry unreachable | Keywords don't trigger a match | Check the matching logic — substring match on `keywords` list |

## Pass criteria

- [ ] All 10 known symptoms match correct KB entries
- [ ] Case-insensitive: `no ads` == `NO ADS` == `No Ads`
- [ ] Unknown symptoms return fallback with common examples
- [ ] Every KB entry reachable by at least one keyword
- [ ] All 3 tools callable on the running server via MCP protocol
