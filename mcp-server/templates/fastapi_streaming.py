"""FastAPI + SSE streaming template.

Uses `{placement_id}`, `{placement}`, and `{format_code}` as substitution slots.
"""

SERVER_CODE = '''\
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from gravity_sdk import Gravity
import json, asyncio

app = FastAPI()

gravity = Gravity(
    # production=True,  # ← uncomment when ready to serve real ads
)

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    # Start the ad request early — it runs in parallel with the LLM stream.
    # get_ads() never raises; on failure it returns AdResult(ads=[]).
    ad_task = asyncio.create_task(
        gravity.get_ads(
            request,
            messages,
            [{{"placement": "{placement}", "placement_id": "{placement_id}"}}],
        )
    )

    async def event_stream():
        # --- Stream your LLM response here ---
        # async for chunk in llm_stream:
        #     yield f"data: {{json.dumps({{\\"text\\": chunk}})}}\\n\\n"

        # After the LLM stream is done, await the ad result and send it.
        result = await ad_task
        ads = [
            {{"adText": a.ad_text, "title": a.title, "cta": a.cta,
              "brandName": a.brand_name, "url": a.url, "favicon": a.favicon,
              "impUrl": a.imp_url, "clickUrl": a.click_url}}
            for a in result.ads
        ]
        yield f"data: {{json.dumps({{\\"type\\": \\"done\\", \\"ads\\": ads}})}}\\n\\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
'''

CLIENT_CODE = '''\
// components/Chat.tsx
import {{ useState }} from 'react';
import {{ gravityContext }} from '@gravity-ai/js';
import {{ GravityAd }} from '@gravity-ai/react';
import type {{ AdResponse }} from '@gravity-ai/react';

export default function Chat() {{
  const [ad, setAd] = useState<AdResponse | null>(null);

  async function sendMessage(messages: {{ role: string; content: string }}[]) {{
    const res = await fetch('/api/chat', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        messages,
        gravity_context: gravityContext({{
          sessionId: 'session-123',
          user: {{ userId: 'user-456' }},
        }}),
      }}),
    }});

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {{
      const {{ done, value }} = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      for (const line of text.split('\\n')) {{
        if (!line.startsWith('data: ')) continue;
        const data = JSON.parse(line.slice(6));
        if (data.type === 'done' && data.ads?.length) {{
          setAd(data.ads[0]);
        }}
      }}
    }}
  }}

  return (
    <div>
      {{/* Your chat UI here */}}
      {format_code}
    </div>
  );
}}
'''
