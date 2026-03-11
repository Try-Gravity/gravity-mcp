"""Curated troubleshooting knowledge base for Gravity ad integration issues."""

TROUBLESHOOT_KB: list[dict[str, str]] = [
    {
        "keywords": "no ads,empty response,empty array,no results,ads not showing",
        "symptom": "No ads returned — empty array or empty response",
        "cause": "The GRAVITY_API_KEY environment variable is missing, empty, or invalid. Without a valid API key, the SDK returns an empty array silently (it never throws).",
        "fix": "1. Verify GRAVITY_API_KEY is set in your server environment.\n2. Check the key at https://trygravity.ai — it should start with 'grav_'.\n3. Ensure the key is passed to the Gravity constructor or available as process.env.GRAVITY_API_KEY.",
        "reference_url": "https://docs.trygravity.ai/quickstart#api-key",
    },
    {
        "keywords": "401,unauthorized,forbidden,403,invalid key,revoked",
        "symptom": "401 Unauthorized or 403 Forbidden response",
        "cause": "The API key is invalid, revoked, or belongs to a different environment (test vs production).",
        "fix": "1. Regenerate your API key at https://trygravity.ai.\n2. Ensure you're using the correct key for your environment.\n3. Check that the Authorization header is formatted as 'Bearer grav_...'.",
        "reference_url": "https://docs.trygravity.ai/quickstart#api-key",
    },
    {
        "keywords": "test ads only,no revenue,not earning,test mode,production",
        "symptom": "Only receiving test ads — no real ads or revenue",
        "cause": "The `production` flag is not set to `true`. By default, the SDK serves test ads with no billing.",
        "fix": "Set `production: true` in your Gravity constructor:\n```\nconst gravity = new Gravity({ production: true });\n```\nOr in Python:\n```\ngravity = Gravity(production=True)\n```\nOnly enable this when you're ready to go live with real ads.",
        "reference_url": "https://docs.trygravity.ai/quickstart#production-mode",
    },
    {
        "keywords": "impressions not tracking,no payout,impUrl,impression not firing,no impression",
        "symptom": "Impressions not tracking — no payout recorded",
        "cause": "The `impUrl` from the ad response is not being fired when the ad becomes visible. The `<GravityAd />` component handles this automatically via IntersectionObserver, but custom implementations must fire it manually.",
        "fix": "For custom implementations, fire a GET request to `ad.impUrl` when the ad enters the viewport:\n```\nfetch(ad.impUrl);\n```\nUsing `<GravityAd />` or `useAdTracking` handles this automatically. Verify the IntersectionObserver is not blocked by CSS (e.g., `display: none` or zero dimensions).",
        "reference_url": "https://docs.trygravity.ai/react#impression-tracking",
    },
    {
        "keywords": "impression expired,impUrl expired,5 minutes,stale",
        "symptom": "Impression URL expired — tracking call rejected",
        "cause": "The `impUrl` must be fired within 5 minutes of the ad response. After that, the URL expires and the impression won't count.",
        "fix": "Fire the impUrl as soon as the ad is displayed to the user. Do not cache ad responses for extended periods. If you need fresh ads, call `getAds()` again.",
        "reference_url": "https://docs.trygravity.ai/react#impression-tracking",
    },
    {
        "keywords": "CORS,cors error,cross-origin,blocked by CORS,access-control",
        "symptom": "CORS error when fetching ads",
        "cause": "The client-side code is calling the Gravity API directly from the browser. The Gravity API is server-to-server only — it does not set CORS headers.",
        "fix": "Move the ad fetch to your server (Express, Next.js API route, FastAPI, etc.) and proxy the response to the client. The SDK's `getAds()` / `gravityAds()` functions are designed to run server-side.",
        "reference_url": "https://docs.trygravity.ai/quickstart#server-side",
    },
    {
        "keywords": "timeout,timed out,slow,timeoutMs,took too long",
        "symptom": "Ad request timing out",
        "cause": "The default timeout is 3000ms. Slow network conditions or large conversation contexts can exceed this. Also check that the ad request is being awaited before the SSE stream ends.",
        "fix": "1. Increase `timeoutMs` (e.g., `new Gravity({ timeoutMs: 5000 })`).\n2. Start the ad request early (before streaming the LLM response) and `await` the promise at the end.\n3. Trim messages to the last 2 turns — the SDK does this automatically.",
        "reference_url": "https://docs.trygravity.ai/quickstart#timeout",
    },
    {
        "keywords": "clickUrl,url,wrong link,landing page,click tracking,ad.url",
        "symptom": "Click tracking not working or wrong landing page",
        "cause": "Using `ad.url` instead of `ad.clickUrl` for the ad link. `ad.url` is the raw landing page; `ad.clickUrl` is the tracking-wrapped URL that records clicks and then redirects.",
        "fix": "Always use `ad.clickUrl` as the `href` for ad links:\n```\n<a href={ad.clickUrl} target=\"_blank\" rel=\"noopener noreferrer sponsored\">\n```\nThe `<GravityAd />` component does this automatically.",
        "reference_url": "https://docs.trygravity.ai/react#click-tracking",
    },
    {
        "keywords": "gravityContext,gravity_context,context missing,missing context,session,device",
        "symptom": "gravity_context missing from request body",
        "cause": "The client is not calling `gravityContext()` and sending it in the request body. The server SDK reads `req.body.gravity_context` to extract session, user, and device information.",
        "fix": "On the client side, call `gravityContext()` and include it in every chat request:\n```\nimport { gravityContext } from '@gravity-ai/js';\n\nconst body = {\n  messages,\n  gravity_context: gravityContext({\n    sessionId: 'your-session-id',\n    user: { userId: 'user-123' },\n  }),\n};\nfetch('/api/chat', { method: 'POST', body: JSON.stringify(body) });\n```",
        "reference_url": "https://docs.trygravity.ai/quickstart#client-context",
    },
    {
        "keywords": "wrong placement,invalid placement,placement error,placement_id,above_response,below_response",
        "symptom": "Invalid placement position — placement rejected or no ads returned",
        "cause": "Using a placement value that is not in the allowed set. Only 5 placements are supported: `above_response`, `below_response`, `inline_response`, `left_response`, `right_response`.",
        "fix": "Use one of the allowed placement values:\n```\nplacements: [\n  { placement: 'below_response', placement_id: 'my-ad-slot' }\n]\n```\nAds must be placed adjacent to AI-generated content only.",
        "reference_url": "https://docs.trygravity.ai/quickstart#placements",
    },
]
