"""Next.js App Router + JSON (non-streaming) template.

Uses `{placement_id}`, `{placement}`, and `{format_code}` as substitution slots.
"""

SERVER_CODE = '''\
// app/api/chat/route.ts
import {{ Gravity }} from '@gravity-ai/api';

const gravity = new Gravity({{
  apiKey: process.env.GRAVITY_API_KEY!,
  // production: true,  // ← uncomment when ready to serve real ads
}});

export async function POST(request: Request) {{
  const body = await request.json();
  const {{ messages }} = body;

  // Fire ad request in parallel with the LLM call.
  // getAds() never throws; on failure it returns {{ ads: [] }}.
  const adPromise = gravity.getAds(
    {{ body, headers: Object.fromEntries(request.headers) }},
    messages,
    [{{ placement: '{placement}', placement_id: '{placement_id}' }}],
  );

  // --- Call your LLM here ---
  // const llmResponse = await generateResponse(messages);

  const {{ ads }} = await adPromise;

  return Response.json({{
    // response: llmResponse,
    ads,
  }});
}}
'''

CLIENT_CODE = '''\
// components/Chat.tsx
'use client';
import {{ useState }} from 'react';
import {{ gravityContext }} from '@gravity-ai/js';
import {{ GravityAd }} from '@gravity-ai/react';
import type {{ AdResponse }} from '@gravity-ai/react';

// TODO: wire these to your app's real session + user identity
const SESSION_ID: string = null!;  // e.g. chatSession.id or route param
const USER_ID: string = null!;     // e.g. currentUser.id from your auth

export default function Chat() {{
  const [ad, setAd] = useState<AdResponse | null>(null);

  async function sendMessage(messages: {{ role: string; content: string }}[]) {{
    const res = await fetch('/api/chat', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        messages,
        gravity_context: gravityContext({{
          sessionId: SESSION_ID,
          user: {{ userId: USER_ID }},
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
