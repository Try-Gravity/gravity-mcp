# MCP Server Live Tool Test Report

Tested all 4 tools via the live MCP stdio transport. 23 smoke tests + 45 unit tests.

---

## 1. `search_formats` — 10 queries


| #   | Query                            | Result                                                     | Status |
| --- | -------------------------------- | ---------------------------------------------------------- | ------ |
| 1   | `detail="names"`, no filters     | Returns 25 format names                                    | PASS   |
| 2   | `detail="summary"`, no filters   | Returns 25 objects with name/description/type              | PASS   |
| 3   | `query="chat"`, summary          | Returns 1 result (bubble) — correct substring match        | PASS   |
| 4   | `category="card"`, names         | Returns 5 card-type formats                                | PASS   |
| 5   | `category="inline"`, summary     | Returns 1 result (compact-bar)                             | PASS   |
| 6   | `query="nonexistent_format_xyz"` | Returns empty array                                        | PASS   |
| 7   | `query="glass"`, full            | Returns code with `backdropFilter`, `WebkitBackdropFilter` | PASS   |
| 8   | `query="link"`, summary          | Returns text-link and hyperlink                            | PASS   |
| 9   | `category="CARD"` (uppercase)    | Returns 5 card-type formats — case-insensitive             | PASS   |
| 10  | No params (defaults)             | Returns all 25 with summary detail                         | PASS   |


### Findings

- **FIXED: Category filter is now case-insensitive.** `category="CARD"` correctly returns the same results as `category="card"`.

---

## 2. `build_theme` — 7 queries


| #   | Input                                                                               | Result                                                          | Status |
| --- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------ |
| 1   | No params (all defaults)                                                            | Light theme, white bg, Zinc palette                             | PASS   |
| 2   | `bg_color="#0f172a"` (dark)                                                         | Correctly detects dark, white text, dark shadow                 | PASS   |
| 3   | Warm light: `bg_color="#FFF7ED"`, `accent="#EA580C"`, `radius=16`, `font="Georgia"` | Correct light detection, custom accent/radius/font applied      | PASS   |
| 4   | All 7 params (dark purple site)                                                     | All explicit values used, nothing auto-derived where overridden | PASS   |
| 5   | Light bg + yellow accent: `bg_color="#F5F5F5"`, `accent="#FFFF00"`                  | CTA text is `#18181B` (dark on yellow) — correct contrast       | PASS   |
| 6   | Invalid input: `bg_color="not-a-color"`                                             | Returns error with "invalid hex" message                        | PASS   |
| 7   | Mid-gray: `bg_color="#808080"`                                                      | Classified as dark (`is_dark=true`) — debatable                 | NOTE   |


### Findings

- **FIXED: Invalid hex input is now rejected.** `bg_color="not-a-color"` returns an error instead of silently producing invalid CSS.
- **NOTE: Mid-gray (#808080) classified as dark.** Its luminance (~0.22) is below the 0.4 threshold so `is_dark=true`. Reasonable but could surprise users with medium-toned sites.

---

## 3. `generate_code` — 13 queries


| #   | Input                                                                           | Result                                                                     | Status |
| --- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------ |
| 1   | card / fastapi / streaming / `placement_id="main"`                              | Clean boilerplate, `placement_id` "main" in server code                    | PASS   |
| 2   | floating / nextjs / non-streaming / `placement_id="main"`                       | Correct template (no SSE), floating style applied                          | PASS   |
| 3   | banner / fastapi / non-streaming / `theme="dark"` / `placement_id="main"`      | Dark theme merged into JSX (not comments)                                  | PASS   |
| 4   | suggestion / nextjs / streaming / explicit tokens / `placement_id="sidebar-1"`  | Theme applied, custom `placement_id` in output                             | PASS   |
| 5   | Invalid format: `"doesnotexist"` / `placement_id="main"`                        | Returns error with full list of valid formats                              | PASS   |
| 6   | card / `placement="above_response"` / `placement_id="top-ad"`                   | Both `above_response` and `top-ad` in server code                          | PASS   |
| 7   | card / dark + overrides (`accent="#E11D48"`, `radius=20`) / `placement_id="main"` | Overrides applied on top of dark preset                                  | PASS   |
| 8   | All 6 page-relative placements / `placement_id="main"`                          | `search_result`, `center_page`, `top_page`, etc. all accepted              | PASS   |
| 9   | `placement="somewhere_invalid"` / `placement_id="main"`                         | Rejected by Pydantic schema — lists all 11 valid placements                | PASS   |
| 10  | Missing `placement_id`                                                          | Rejected by Pydantic schema — "Missing required argument"                  | PASS   |
| 11  | `placement_id="has spaces!"`                                                    | Rejected — "Must be 1-64 alphanumeric characters, hyphens, or underscores" | PASS   |
| 12  | `placement_id=""` (empty)                                                       | Rejected — validation error                                                | PASS   |
| 13  | hyperlink / nextjs / streaming / `placement_id="main"`                          | Uses `<AdText>` component (correct for hyperlink variant)                  | PASS   |


### Findings

- **FIXED: Theme is now merged directly into the `<GravityAd>` JSX**, not appended as comments. `style` and `slotProps` are injected inline.
- **FIXED: `placement` is now a Literal enum** with 11 values matching the Gravity engine and dashboard UI. Invalid values are rejected at the schema level before the function runs.
- **NEW: `placement_id` is now a required parameter** (no default). The agent must provide a publisher-confirmed tracking ID. Validated for format (alphanumeric + hyphens/underscores, 1-64 chars).
- **NEW: The `integrate_gravity_ads` prompt** instructs the agent to confirm `placement` and `placement_id` with the publisher before generating code (step 3).
- Server code creates a new `app = FastAPI()` every time. Templates are greenfield scaffolds — this is by design for starter code.

### Placement Enforcement

| Constraint                  | Enforcement Level     | Behavior on Violation                              |
| --------------------------- | --------------------- | -------------------------------------------------- |
| `placement_id` required     | MCP schema (Pydantic) | `Missing required argument` before function runs   |
| `placement_id` format       | Runtime validation    | Error with format requirements                     |
| `placement` enum (11 vals)  | MCP schema (Pydantic) | `Input should be '...' or '...'` — lists all valid |
| `placement` invalid string  | MCP schema (Pydantic) | Rejected before function runs                      |

---

## 4. `troubleshoot` — 10 queries


| #   | Symptom                                    | Matched?                            | Status |
| --- | ------------------------------------------ | ----------------------------------- | ------ |
| 1   | `"no ads showing"`                         | Yes — API key issue                 | PASS   |
| 2   | `"401 unauthorized error"`                 | Yes — invalid/revoked key           | PASS   |
| 3   | `"CORS error in browser console"`          | Yes — server-side only              | PASS   |
| 4   | `"ads load but clicks don't track"`        | Yes — clickUrl issue                | PASS   |
| 5   | `"impressions not counting"`               | Yes — impression tracking           | PASS   |
| 6   | `"test ads"`                               | Yes — production flag               | PASS   |
| 7   | `"impUrl"` (exact keyword)                 | Yes — impression tracking           | PASS   |
| 8   | `"the ad link goes to the wrong page"`     | Yes — clickUrl/landing page         | PASS   |
| 9   | `"gravity_context not being sent"`         | Yes — via `gravity_context` keyword | PASS   |
| 10  | `"my ads are timed out and loading slow"`  | Yes — via `timed out` keyword       | PASS   |


### Findings

- **FIXED: Fuzzy matching now handles natural-language symptom descriptions.** Previous brittle keyword matching has been improved — all 10 test queries match correctly.

---

## Summary


| Tool           | Queries | Pass   | Fail/Bug     | Pass Rate |
| -------------- | ------- | ------ | ------------ | --------- |
| search_formats | 10      | 10     | 0            | 100%      |
| build_theme    | 7       | 6      | 1 note       | 86%       |
| generate_code  | 13      | 13     | 0            | 100%      |
| troubleshoot   | 10      | 10     | 0            | 100%      |
| **Total**      | **40**  | **39** | **1 note**   | **98%**   |


## Issues Fixed Since Last Report

1. ~~`search_formats` category filter is case-sensitive~~ — **FIXED** (normalized to lowercase)
2. ~~`build_theme` accepts invalid color input silently~~ — **FIXED** (validates hex format, returns error)
3. ~~`generate_code` theme is appended as comments, not merged~~ — **FIXED** (theme merged into JSX)
4. ~~`generate_code` hardcodes `below_response` placement~~ — **FIXED** (`placement` is now a Literal enum with 11 values)
5. ~~`troubleshoot` keyword matching is too narrow (54% hit rate)~~ — **FIXED** (fuzzy matching improved)
6. **NEW: `placement_id` is now required** — no auto-generated UUIDs. Agent must confirm with publisher.
7. **NEW: `placement` is a schema-enforced enum** — 11 values matching the Gravity engine/dashboard.

## Remaining Notes

- Mid-gray (#808080) classified as dark — luminance below 0.4 threshold. Reasonable behavior.
- Templates are greenfield scaffolds (new `app = FastAPI()`). By design for starter code.
