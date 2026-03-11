"""Resource templates for Gravity SDK documentation and format catalog."""

from __future__ import annotations

import json

from resources.format_catalog import FORMAT_CATALOG

# ---------------------------------------------------------------------------
# Doc topics — verbatim content from the SDK source files
# ---------------------------------------------------------------------------

DOC_TOPICS: dict[str, str] = {
    "ad-response": """\
# Ad Response Interface

The `Ad` interface represents a single ad object returned by the Gravity API.

```typescript
export interface Ad {
  /** The advertisement copy text */
  adText: string;
  /** Ad title */
  title?: string;
  /** Call-to-action text (e.g., 'Learn More', 'Shop Now') */
  cta?: string;
  /** Brand/advertiser name */
  brandName?: string;
  /** Landing page URL */
  url?: string;
  /** Favicon URL */
  favicon?: string;
  /** Impression tracking URL - fire this when ad is displayed */
  impUrl?: string;
  /** Click-through tracking URL - use this as href for ad clicks */
  clickUrl?: string;
}
```

**Important:** Always use `ad.clickUrl` (not `ad.url`) for the ad link — it includes click tracking.
Fire a GET to `ad.impUrl` when the ad becomes visible (within 5 minutes of receiving it).
""",
    "styling": """\
# Styling `<GravityAd />`

## How it works

`<GravityAd />` uses **inline styles on every element**. There are no injected stylesheets, no CSS class names, and no CSS custom properties. Every visual value is a plain `React.CSSProperties` object that you can read, override, or replace.

## DOM structure

```
a                                ← outer link (container)
  div                            ← inner padding/layout wrapper
    div                          ← header row
      img                        ← favicon
      span                       ← brand name
      span                       ← "Sponsored" label
    div                          ← body
      p                          ← title
      p                          ← ad text
    span                         ← CTA button

Inline variant:
  a
    div                          ← inner (row layout)
      div                        ← content column
        div                      ← header
        div                      ← body
      span                       ← CTA (right-aligned)
```

## Method 1: `style` prop

Override the outer container directly:

```tsx
<GravityAd ad={ad} style={{ maxWidth: 400, borderRadius: 16 }} />
```

## Method 2: `slotProps`

Target any inner element by name:

```tsx
<GravityAd
  ad={ad}
  slotProps={{
    cta: { style: { background: '#E11D48', borderRadius: 999 } },
    label: { style: { display: 'none' } },
    inner: { style: { padding: '20px 24px' } },
  }}
/>
```

Slot keys: `container`, `inner`, `header`, `favicon`, `brand`, `label`, `body`, `title`, `text`, `cta`.

Each accepts `{ style?: CSSProperties; className?: string }`.

## Method 3: `className` prop

Add a CSS class to the outer container or any slot for external stylesheet overrides:

```tsx
<GravityAd ad={ad} className="my-ad" />

<GravityAd
  ad={ad}
  slotProps={{
    cta: { className: 'my-cta-override' },
  }}
/>
```

## Default values

| Element | Key properties |
|---------|---------------|
| Container | `background: '#FFFFFF'`, `border: '1px solid #E4E4E7'`, `borderRadius: 10`, `boxShadow: '0 1px 2px ...'` |
| Inner | `padding: '14px 16px 16px'`, `gap: 10` |
| Brand | `fontSize: 13`, `fontWeight: 600`, `color: '#18181B'` |
| Label | `fontSize: 10`, `textTransform: 'uppercase'`, `color: '#71717A'`, `border: '1px solid #E4E4E7'` |
| Title | `fontSize: 14`, `fontWeight: 500`, `color: '#18181B'` |
| Text | `fontSize: 13`, `color: '#71717A'` |
| CTA | `background: '#2563EB'`, `color: '#FFFFFF'`, `borderRadius: 6`, `padding: '7px 16px'` |

## Common recipes

### Dark mode

```tsx
<GravityAd
  ad={ad}
  style={{
    background: '#18181B',
    color: '#FAFAFA',
    border: '1px solid #3F3F46',
    boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
  }}
  slotProps={{
    brand: { style: { color: '#FAFAFA' } },
    title: { style: { color: '#FAFAFA' } },
    text: { style: { color: '#A1A1AA' } },
    label: { style: { color: '#A1A1AA', border: '1px solid #3F3F46' } },
    cta: { style: { background: '#3B82F6' } },
  }}
/>
```

### Match your brand color

```tsx
<GravityAd
  ad={ad}
  slotProps={{
    cta: { style: { background: '#E11D48' } },
  }}
/>
```

### Hide the label

```tsx
<GravityAd ad={ad} showLabel={false} />
```

### Full-width CTA

```tsx
<GravityAd
  ad={ad}
  slotProps={{
    cta: { style: { alignSelf: 'stretch', textAlign: 'center' } },
  }}
/>
```

## Escape hatches

**`<AdText />`** — Renders only `ad.adText` as a plain link/span with zero built-in styles.

**`useAdTracking`** — Build your own component from scratch. The hook handles impression and click tracking.

```tsx
import { useAdTracking } from '@gravity-ai/react';

function MyAd({ ad }) {
  const { containerRef, handleClick } = useAdTracking({ ad });

  return (
    <a ref={containerRef} href={ad.clickUrl} onClick={handleClick}>
      {/* render whatever you want */}
    </a>
  );
}
```
""",
    "react-component": """\
# React Component Types

```typescript
import type { CSSProperties, ReactNode } from 'react';

export interface AdResponse {
  adText: string;
  title?: string;
  cta?: string;
  brandName?: string;
  url?: string;
  favicon?: string;
  impUrl?: string;
  clickUrl?: string;
}

export type GravityAdVariant = 'card' | 'inline' | 'minimal';

export interface GravityAdSlotProps {
  /** Outer `<a>` wrapper */
  container?: { style?: CSSProperties; className?: string };
  /** Inner padding/layout wrapper */
  inner?: { style?: CSSProperties; className?: string };
  /** Header row (favicon + brand + label) */
  header?: { style?: CSSProperties; className?: string };
  /** Favicon `<img>` */
  favicon?: { style?: CSSProperties; className?: string };
  /** Brand name `<span>` */
  brand?: { style?: CSSProperties; className?: string };
  /** "Sponsored" label `<span>` */
  label?: { style?: CSSProperties; className?: string };
  /** Body wrapper (title + text) */
  body?: { style?: CSSProperties; className?: string };
  /** Title `<p>` */
  title?: { style?: CSSProperties; className?: string };
  /** Ad text `<p>` */
  text?: { style?: CSSProperties; className?: string };
  /** CTA button `<span>` */
  cta?: { style?: CSSProperties; className?: string };
}

export interface GravityAdProps {
  ad: AdResponse | null;
  variant?: GravityAdVariant;
  className?: string;
  style?: CSSProperties;
  slotProps?: GravityAdSlotProps;
  showLabel?: boolean;
  labelText?: string;
  onClick?: () => void;
  onImpression?: () => void;
  onClickTracked?: () => void;
  fallback?: ReactNode;
  disableImpressionTracking?: boolean;
  openInNewTab?: boolean;
}

export interface AdTextProps {
  ad: AdResponse | null;
  className?: string;
  style?: CSSProperties;
  onClick?: () => void;
  onImpression?: () => void;
  onClickTracked?: () => void;
  fallback?: ReactNode;
  disableImpressionTracking?: boolean;
  openInNewTab?: boolean;
}
```
""",
    "server-sdk": """\
# Python Server SDK — `gravity-sdk`

```python
from gravity_sdk import Gravity

gravity = Gravity(production=True)  # reads GRAVITY_API_KEY from env

result = await gravity.get_ads(request, messages, placements)
```

## `Gravity` class

```python
class Gravity:
    \"\"\"Async client for the Gravity API.

    Args:
        api_key:     Gravity API key. Defaults to the GRAVITY_API_KEY env var.
        api_url:     Gravity API endpoint URL.
        timeout:     Request timeout in seconds (default: 3.0).
        production:  When True, serves real ads. Defaults to False (test ads).
        relevancy:   Minimum relevancy threshold (0.0-1.0). Default: 0.2.
    \"\"\"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_url: str = "https://server.trygravity.ai/api/v1/ad",
        timeout: float = 3.0,
        production: bool = False,
        relevancy: float = 0.2,
    ) -> None: ...

    async def get_ads(
        self,
        request: Any,
        messages: list[dict[str, Any]],
        placements: list[dict[str, str]],
        *,
        production: bool | None = None,
        relevancy: float | None = None,
    ) -> AdResult:
        \"\"\"Request ads from the Gravity API.

        Never raises — returns AdResult(ads=[]) on any failure.

        Args:
            request:    The framework request object (FastAPI, Django, Flask, etc.).
            messages:   Conversation messages [{"role": ..., "content": ...}].
            placements: Ad placements, e.g.
                        [{"placement": "below_response", "placement_id": "main"}].
            production: Override the constructor-level production flag.
            relevancy:  Override the constructor-level relevancy threshold.
        \"\"\"
```

## Context manager usage

```python
async with Gravity(production=True) as gravity:
    result = await gravity.get_ads(request, messages, placements)
    for ad in result.ads:
        print(ad.ad_text, ad.click_url)
```
""",
    "js-sdk": """\
# JavaScript/TypeScript Server SDK — `@gravity-ai/api`

## `Gravity` class

```typescript
import { Gravity } from '@gravity-ai/api';

const gravity = new Gravity({ production: true });

app.post('/api/chat', async (req, res) => {
  const { messages } = req.body;
  const adPromise = gravity.getAds(req, messages, [
    { placement: 'below_response', placement_id: 'main' },
  ]);

  // stream your LLM response...

  const { ads } = await adPromise;
  res.write(`data: ${JSON.stringify({ type: 'done', ads })}\\n\\n`);
  res.end();
});
```

### Constructor options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | `string` | `process.env.GRAVITY_API_KEY` | Gravity API key |
| `production` | `boolean` | `false` | `true` = real ads, `false` = test ads (no billing) |
| `relevancy` | `number` | `0.2` | Minimum relevancy threshold (0-1) |
| `timeoutMs` | `number` | `3000` | Request timeout in ms |
| `excludedTopics` | `string[]` | — | Topics to exclude from ad matching |

### `getAds()` — never throws

```typescript
async getAds(
  req: IncomingAdRequest,
  messages: MessageObject[],
  placements: PlacementObject[],
  overrides?: GravityAdsOptions,
): Promise<GravityAdsResult>
```

Returns: `{ ads: Ad[], status: number, elapsed: string, requestBody, error? }`

## `gravityAds()` function (standalone)

```typescript
import { gravityAds } from '@gravity-ai/api';

const { ads } = await gravityAds(req, messages, placements, { production: true });
```

## Client-side context

```typescript
import { gravityContext } from '@gravity-ai/js';

const body = {
  messages,
  gravity_context: gravityContext({
    sessionId: 'session-123',
    user: { userId: 'user-456' },
  }),
};
fetch('/api/chat', { method: 'POST', body: JSON.stringify(body) });
```
""",
    "placement-policy": """\
# Placement Policy

## Allowed placements

```typescript
export type Placement =
  | 'above_response'
  | 'below_response'
  | 'inline_response'
  | 'left_response'
  | 'right_response';
```

## Rules

1. **Adjacent to AI content only** — Ads must be placed next to AI-generated responses, not in static page areas.
2. **1-10 placements per request** — Each `getAds()` call accepts an array of 1-10 placement objects.
3. **Unique placement_id** — Each placement needs a unique `placement_id` for tracking and analytics.

## Placement object

```typescript
export interface PlacementObject {
  placement: Placement;    // Position relative to the AI response
  placement_id: string;    // Unique tracking ID for this ad slot
}
```

## Example

```typescript
const { ads } = await gravity.getAds(req, messages, [
  { placement: 'above_response', placement_id: 'top-ad' },
  { placement: 'below_response', placement_id: 'bottom-ad' },
]);
```
""",
    "checklist": """\
# Integration Checklist

Use this to verify your Gravity ad integration is complete and correct.

## Server-side

- [ ] **API key set** — `GRAVITY_API_KEY` environment variable is configured
- [ ] **Server-side fetch** — `getAds()` / `get_ads()` is called from your server, not the client
- [ ] **Parallel request** — Ad request starts before/alongside the LLM stream (not after)
- [ ] **Never throws** — `getAds()` never throws; check `ads.length` before rendering
- [ ] **Context forwarded** — Client sends `gravity_context` in request body, server passes `req` to `getAds()`
- [ ] **Placement IDs** — Each placement has a unique `placement_id`

## Client-side

- [ ] **gravityContext()** — Client calls `gravityContext({ sessionId, user: { userId } })` and sends it in the request body
- [ ] **Component renders** — `<GravityAd ad={ad} />` renders when `ad` is not null
- [ ] **clickUrl used** — Ad links use `ad.clickUrl` (not `ad.url`) for click tracking
- [ ] **Impression fires** — `impUrl` GET fires when ad is visible (automatic with `<GravityAd />`, manual with custom components)
- [ ] **Impression timing** — `impUrl` is fired within 5 minutes of receiving the ad

## Going live

- [ ] **Test ads work** — Integration works with `production: false` (default)
- [ ] **Production flag** — Set `production: true` when ready to serve real ads and earn revenue
- [ ] **Error handling** — App works gracefully when no ads are returned (empty array)
""",
}


def get_formats_index() -> str:
    """Return a formatted index of all 25 ad formats."""
    lines = []
    for entry in FORMAT_CATALOG.values():
        lines.append(f"- **{entry['name']}** ({entry['type']}) — {entry['description']}")
    return "# Gravity Ad Formats\n\n" + "\n".join(lines)


def get_format_detail(name: str) -> str | None:
    """Return full detail for a single format, or None if not found."""
    entry = FORMAT_CATALOG.get(name)
    if not entry:
        return None
    return json.dumps(entry, indent=2)


def get_doc_topic(topic: str) -> str | None:
    """Return documentation for a topic, or None if not found."""
    return DOC_TOPICS.get(topic)
