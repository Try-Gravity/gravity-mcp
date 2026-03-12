"""FastAPI + JSON (non-streaming) template.

Uses `{placement_id}`, `{placement}`, and `{format_code}` as substitution slots.
"""

SERVER_CODE = '''\
# main.py
from fastapi import FastAPI, Request
from gravity_sdk import Gravity
import os

app = FastAPI()

gravity = Gravity(
    api_key=os.environ["GRAVITY_API_KEY"],
    # production=True,  # ← uncomment when ready to serve real ads
)

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    # get_ads() never raises; on failure it returns AdResult(ads=[]).
    result = await gravity.get_ads(
        request,
        messages,
        [{{"placement": "{placement}", "placement_id": "{placement_id}"}}],
    )

    ads = [
        {{"adText": a.ad_text, "title": a.title, "cta": a.cta,
          "brandName": a.brand_name, "url": a.url, "favicon": a.favicon,
          "impUrl": a.imp_url, "clickUrl": a.click_url}}
        for a in result.ads
    ]

    return {{
        # "response": llm_response,
        "ads": ads,
    }}
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

    const data = await res.json();
    if (data.ads?.length) {{
      setAd(data.ads[0]);
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
