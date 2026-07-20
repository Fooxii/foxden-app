import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const DAILY_MESSAGE_CAP = 5
// verify this against the free model list in your actual Ollama Cloud
// dashboard before first use — the exact free-tier lineup isn't
// consistently documented, so don't assume this name is still current
const OLLAMA_MODEL = 'llama3.2:cloud'

const FOXDEN_KNOWLEDGE = `
FoxDen is a personalized news feed app. Users follow "tags" — official
topics (like Gaming, AI, Sports) or their own custom tags they create —
and the feed shows articles matched to those tags.

Key features:
- Feed page: shows a mixed feed of articles and story clusters from all
  followed tags. Click the search bar at the top to browse and follow
  more official or custom tags.
- Pinning: click a followed tag's pill in the filter bar to narrow the
  feed to only that tag. Click again to unpin. Only one tag can be
  pinned at a time.
- Unfollowing: click the × on a tag's pill in the filter bar.
- Sorting: toggle between "Relevance" and "Recency" above the feed.
- Story clusters: when multiple sources cover the same story, they're
  grouped into one card with a source count badge — click to expand.
- Custom tags: created from the Profile page. Give it a name and
  describe what it should cover; it usually starts matching within
  about a minute.
- Account settings: on the Profile page — theme, deleting custom tags,
  deleting your account.
- Password: "Forgot password?" on the login page, or change it from
  Profile → Settings while logged in.
`.trim()

Deno.serve(async (req) => {
  const authHeader = req.headers.get('Authorization')
  if (!authHeader) {
    return new Response(JSON.stringify({ error: 'Missing authorization' }), { status: 401 })
  }

  const userClient = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,
    { global: { headers: { Authorization: authHeader } } }
  )

  const { data: { user }, error: userError } = await userClient.auth.getUser()
  if (userError || !user) {
    return new Response(JSON.stringify({ error: 'Invalid session' }), { status: 401 })
  }

  const { message, history } = await req.json()
  if (!message || typeof message !== 'string') {
    return new Response(JSON.stringify({ error: 'Missing message' }), { status: 400 })
  }

  const adminClient = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  const today = new Date().toISOString().split('T')[0]

  const { data: usageRow } = await adminClient
    .from('chat_usage')
    .select('message_count')
    .eq('user_id', user.id)
    .eq('message_date', today)
    .maybeSingle()

  const currentCount = usageRow?.message_count ?? 0

  if (currentCount >= DAILY_MESSAGE_CAP) {
    return new Response(
      JSON.stringify({ error: `You've reached your limit of ${DAILY_MESSAGE_CAP} messages for today. Try again tomorrow.` }),
      { status: 429 }
    )
  }

  const messages = [
    {
      role: 'system',
      content:
        'You are the FoxDen assistant. Answer ONLY using the information below about ' +
        'the FoxDen app. If the question is not covered by this information, say you ' +
        "don't have that information rather than guessing or answering from general " +
        `knowledge. Keep answers short and direct.\n\n${FOXDEN_KNOWLEDGE}`
    },
    ...(Array.isArray(history) ? history.slice(-6) : []),
    { role: 'user', content: message }
  ]

  const ollamaResponse = await fetch('https://api.ollama.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('OLLAMA_API_KEY')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model: OLLAMA_MODEL, messages, stream: false })
  })

  if (!ollamaResponse.ok) {
    const errText = await ollamaResponse.text()
    return new Response(JSON.stringify({ error: `Assistant is temporarily unavailable: ${errText}` }), { status: 502 })
  }

  const result = await ollamaResponse.json()
  const reply = result.choices?.[0]?.message?.content ?? "Sorry, I couldn't generate a response."

  await adminClient
    .from('chat_usage')
    .upsert(
      { user_id: user.id, message_date: today, message_count: currentCount + 1 },
      { onConflict: 'user_id,message_date' }
    )

  return new Response(
    JSON.stringify({ reply, remaining: DAILY_MESSAGE_CAP - (currentCount + 1) }),
    { status: 200 }
  )
})
