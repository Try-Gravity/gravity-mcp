"""Next.js App Router + SSE streaming template.

Uses `{placement_id}`, `{placement}`, and `{format_code}` as substitution slots.
"""

SERVER_CODE = '''\
// app/api/chat/route.ts
import {{ Gravity }} from '@gravity-ai/api';

const gravity = new Gravity({{
  // production: true,  // ← uncomment when ready to serve real ads
}});

export async function POST(request: Request) {{
  const body = await request.json();
  const {{ messages }} = body;

  // Start the ad request early — it runs in parallel with the LLM stream.
  // getAds() never throws; on failure it returns {{ ads: [] }}.
  const adPromise = gravity.getAds(
    {{ body, headers: Object.fromEntries(request.headers) }},
    messages,
    [{{ placement: '{placement}', placement_id: '{placement_id}' }}],
  );

  const encoder = new TextEncoder();
  const stream = new ReadableStream({{
    async start(controller) {{
      // --- Stream your LLM response here ---
      // Example: for await (const chunk of llmStream) {{
      //   controller.enqueue(encoder.encode(`data: ${{JSON.stringify({{ text: chunk }})}}\\n\\n`));
      // }}

      // After the LLM stream is done, await the ad result and send it.
      const {{ ads }} = await adPromise;
      controller.enqueue(
        encoder.encode(`data: ${{JSON.stringify({{ type: 'done', ads }})}}\\n\\n`),
      );
      controller.close();
    }},
  }});

  return new Response(stream, {{
    headers: {{
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    }},
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
