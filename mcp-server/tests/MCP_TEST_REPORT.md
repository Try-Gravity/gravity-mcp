# MCP Server Live Tool Test Report

Tested all 4 tools via the live MCP stdio transport. 30 total queries.

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
| 9   | `category="CARD"` (uppercase)    | Returns empty — **case-sensitive, no match**               | BUG    |
| 10  | No params (defaults)             | Returns all 25 with summary detail                         | PASS   |


### Findings

- **BUG: Category filter is case-sensitive.** `category="CARD"` returns nothing while `category="card"` returns 5 results. The LLM might pass uppercase categories since the tool description uses quoted examples. Should normalize with `.lower()`.
- Multi-word queries like `"inline link text"` return empty because the match is substring-based and the full phrase doesn't appear in any single name+description. This is expected behavior but worth noting — a word-level OR match would be more useful.

---

## 2. `build_theme` — 7 queries


| #   | Input                                                                               | Result                                                          | Status |
| --- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------ |
| 1   | No params (all defaults)                                                            | Light theme, white bg, Zinc palette                             | PASS   |
| 2   | `bg_color="#0f172a"` (dark)                                                         | Correctly detects dark, white text, dark shadow                 | PASS   |
| 3   | Warm light: `bg_color="#FFF7ED"`, `accent="#EA580C"`, `radius=16`, `font="Georgia"` | Correct light detection, custom accent/radius/font applied      | PASS   |
| 4   | All 7 params (dark purple site)                                                     | All explicit values used, nothing auto-derived where overridden | PASS   |
| 5   | Light bg + yellow accent: `bg_color="#F5F5F5"`, `accent="#FFFF00"`                  | CTA text is `#18181B` (dark on yellow) — correct contrast       | PASS   |
| 6   | Invalid input: `bg_color="not-a-color"`                                             | **No error — passes `"not-a-color"` into `style.background`**   | BUG    |
| 7   | Mid-gray: `bg_color="#808080"`                                                      | Classified as dark (`is_dark=true`) — debatable                 | NOTE   |


### Findings

- **BUG: No input validation.** `bg_color="not-a-color"` silently produces a theme with `background: 'not-a-color'` — invalid CSS that would fail at render. Should return an error or at least a warning.
- **NOTE: Mid-gray (#808080) classified as dark.** Its luminance (~0.22) is below the 0.4 threshold so `is_dark=true`. This means it gets white text and dark-mode shadows. Reasonable but could surprise users with medium-toned sites.
- The `code_snippet` output has `borderRadius: '10'` (string) instead of `borderRadius: 10` (number) — the JSX would render correctly but it's inconsistent with the `style` dict which uses an integer.

---

## 3. `generate_code` — 7 queries


| #   | Input                                                                           | Result                                                          | Status |
| --- | ------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------ |
| 1   | card / fastapi / streaming / no theme                                           | Clean boilerplate, `placement_id` in both server+client         | PASS   |
| 2   | floating / nextjs / non-streaming                                               | Correct template (no SSE, `res.json()`), floating style applied | PASS   |
| 3   | banner / fastapi / non-streaming / `theme="dark"`                               | Dark theme snippet appended as comment block                    | PASS   |
| 4   | suggestion / nextjs / streaming / explicit tokens                               | Theme applied with custom colors, font, radius                  | PASS   |
| 5   | Invalid format: `"doesnotexist"`                                                | Returns error with full list of valid formats                   | PASS   |
| 6   | hyperlink / nextjs / streaming                                                  | Uses `<AdText>` component (correct for hyperlink variant)       | PASS   |
| 7   | card / fastapi / streaming / dark + overrides (`accent="#E11D48"`, `radius=20`) | Overrides applied on top of dark preset                         | PASS   |


### Findings

- **Theme is appended as comments, not merged into the component.** When theme tokens are passed, `generate_code` appends theme overrides as a separate comment block (`// Theme overrides (auto-matched to site):`) below the component. The `<GravityAd>` in the actual JSX retains the format's default styles. The LLM user has to manually merge these, which is error-prone.
- **Server code creates a new `app = FastAPI()` every time.** There's no parameter to integrate into an existing app. Templates are always greenfield scaffolds.
- `**placement` is always hardcoded to `"below_response"`.** There's no parameter to specify placement position. All 4 templates use the same placement.
- **No `'use client'` in FastAPI client template.** The NextJS template correctly includes `'use client'` but FastAPI's client template omits it — this is technically correct (FastAPI doesn't use Next.js conventions) but the client code is React either way.

---

## 4. `troubleshoot` — 10 queries


| #   | Symptom                                    | Matched?                            | Status |
| --- | ------------------------------------------ | ----------------------------------- | ------ |
| 1   | `"no ads showing"`                         | Yes — API key issue                 | PASS   |
| 2   | `"401 unauthorized error"`                 | Yes — invalid/revoked key           | PASS   |
| 3   | `"CORS error in browser console"`          | Yes — server-side only              | PASS   |
| 4   | `"ads load but clicks don't track"`        | No — falls to generic               | FAIL   |
| 5   | `"impressions not counting"`               | No — falls to generic               | FAIL   |
| 6   | `"impression"` (single keyword)            | No — falls to generic               | FAIL   |
| 7   | `"impUrl"` (exact keyword)                 | Yes — impression tracking           | PASS   |
| 8   | `"test ads"` (matches KB keyword fragment) | No — falls to generic               | FAIL   |
| 9   | `"only getting test ads, no real ones"`    | No — falls to generic               | FAIL   |
| 10  | `"the ad link goes to the wrong page"`     | No — falls to generic               | FAIL   |
| 11  | `"using ad.url but clicks aren't tracked"` | Yes — via `ad.url` keyword          | PASS   |
| 12  | `"gravity_context not being sent"`         | Yes — via `gravity_context` keyword | PASS   |
| 13  | `"my ads are timed out and loading slow"`  | Yes — via `timed out` keyword       | PASS   |


### Findings

- **Keyword matching is too brittle.** 6 of 13 natural-language queries missed. The tool uses exact substring matching against a comma-separated keyword list. This fails for:
  - **Synonyms / rephrasings**: `"clicks don't track"` doesn't match any keyword for the clickUrl entry (needs `"click tracking"` or `"ad.url"`)
  - **Partial keyword matches**: `"test ads"` doesn't match `"test ads only"` because the keyword is `"test ads only"` — but the match logic checks `kw in symptom_lower`, not `symptom_lower in kw`. So `"test ads"` fails because no keyword is a substring of `"test ads"`.
  - Wait — actually `"test ads only"` IS in the keywords, and the check is `kw in symptom_lower`. So `"test ads only" in "test ads"` → False because `"test ads"` is shorter. The user input needs to CONTAIN the keyword, not vice versa. This means short user inputs systematically fail.
  - `"impression"` (7 chars) fails because no keyword is that short — the shortest is `"impUrl"` (6 chars) which doesn't match `"impression"`.
- **The fallback is unhelpful.** Every miss returns the same generic "Contact support" message with the same 5 bullet points. No attempt at fuzzy matching or suggesting the closest KB entry.

---

## Summary


| Tool           | Queries | Pass   | Fail/Bug                        | Pass Rate |
| -------------- | ------- | ------ | ------------------------------- | --------- |
| search_formats | 10      | 9      | 1 (case-sensitive category)     | 90%       |
| build_theme    | 7       | 5      | 1 bug + 1 note                  | 71%       |
| generate_code  | 7       | 7      | 0 bugs, 4 design notes          | 100%      |
| troubleshoot   | 13      | 7      | 6 (keyword matching too narrow) | 54%       |
| **Total**      | **37**  | **28** | **9**                           | **76%**   |


## Priority Issues

1. `**troubleshoot` keyword matching is too narrow (54% hit rate).** Natural-language symptom descriptions frequently miss. Needs fuzzy matching, stemming, or at minimum more keyword synonyms.
2. `**build_theme` accepts invalid color input silently.** Should validate hex format and return an error.
3. `**search_formats` category filter is case-sensitive.** Should normalize to lowercase.
4. `**generate_code` theme is appended as comments, not merged.** The theme `style`/`slotProps` should be injected directly into the `<GravityAd>` JSX, not left as a separate comment for manual merging.
5. `**generate_code` hardcodes `below_response` placement.** Should accept a `placement` parameter.

