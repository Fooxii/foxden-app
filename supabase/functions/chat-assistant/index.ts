import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const DAILY_MESSAGE_CAP = 5
const OLLAMA_MODEL = 'gpt-oss:20b'

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

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

async function fetchUserContext(adminClient: any, userId: string) {
  const ctx: any = {
    username: null,
    fullName: null,
    followedTags: [],
    recentArticles: [],
    totalArticles: null,
  }

  const { data: profile } = await adminClient
    .from('users')
    .select('name')
    .eq('id', userId)
    .single()

  if (profile) {
    ctx.username = profile.name || null
    ctx.fullName = profile.name || null
  }

  const { data: tagRows } = await adminClient
    .from('user_tags')
    .select('is_pinned, tags(name)')
    .eq('user_id', userId)

  if (tagRows) {
    ctx.followedTags = tagRows
      .map((r: any) => ({ name: r.tags?.name, isPinned: r.is_pinned }))
      .filter((t: any) => t.name)
  }

  const { count } = await adminClient
    .from('articles')
    .select('*', { count: 'exact', head: true })
  ctx.totalArticles = count

  const { data: userTagIds } = await adminClient
    .from('user_tags')
    .select('tag_id')
    .eq('user_id', userId)

  const tagIds = userTagIds?.map((r: any) => r.tag_id) || []
  if (tagIds.length === 0) return ctx

  const { data: articleTagRows } = await adminClient
    .from('article_tags')
    .select('article_id')
    .in('tag_id', tagIds)

  const articleIds = [...new Set(articleTagRows?.map((r: any) => r.article_id) || [])]
  if (articleIds.length === 0) return ctx

  const { data: articles } = await adminClient
    .from('articles')
    .select(`
      id,
      title,
      published_at,
      story_clusters(headline, source_count),
      sources(name)
    `)
    .in('id', articleIds)
    .order('published_at', { ascending: false })
    .limit(5)

  if (articles) {
    ctx.recentArticles = articles.map((a: any) => ({
      title: a.title,
      source: a.sources?.name || null,
      clusterHeadline: a.story_clusters?.headline || null,
      clusterSourceCount: a.story_clusters?.source_count || null,
      publishedAt: a.published_at,
    }))
  }

  return ctx
}

function buildSystemPrompt(ctx: any) {
  let prompt = 'You are the FoxDen assistant.'
  if (ctx.username) prompt += ` You are currently helping ${ctx.username}.`

  prompt += '\n\nUser context:'
  if (ctx.username) prompt += `\n- Name: ${ctx.username}`

  if (ctx.followedTags.length > 0) {
    const pinned = ctx.followedTags.find((t: any) => t.isPinned)
    prompt += `\n- Followed tags: ${ctx.followedTags.map((t: any) => t.name).join(', ')}`
    if (pinned) prompt += `\n- Currently pinned tag: ${pinned.name}`
  } else {
    prompt += '\n- Followed tags: (none yet — the user can follow tags from the search bar)'
  }

  if (ctx.recentArticles.length > 0) {
    prompt += '\n- Recent articles in their feed:'
    ctx.recentArticles.forEach((a: any) => {
      if (a.clusterHeadline && a.clusterSourceCount > 1) {
        prompt += `\n  • Story cluster: "${a.clusterHeadline}" (${a.clusterSourceCount} sources)`
      } else {
        prompt += `\n  • "${a.title}"${a.source ? ` — ${a.source}` : ''}`
      }
    })
  } else {
    prompt += '\n- Recent articles: (feed is empty or no articles matched yet)'
  }

  if (ctx.totalArticles !== null) {
    prompt += `\n- Total articles available on FoxDen: ${ctx.totalArticles.toLocaleString()}`
  }

  prompt += `\n\nApp knowledge:\n${FOXDEN_KNOWLEDGE}`

  prompt += `\n\nRules:
- Answer ONLY using the information above about FoxDen and this user's personal context.
- If asked about something not covered, say you don't have that information.
- Never guess, hallucinate, or use outside knowledge.
- Never reveal information about other users.
- Your answers should be short, direct and to the point.`

  return prompt
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
    const SUPABASE_ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY')!
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const OLLAMA_API_KEY = Deno.env.get('OLLAMA_API_KEY')!

    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Missing authorization' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: authHeader } }
    })

    const { data: { user }, error: userError } = await userClient.auth.getUser()
    if (userError || !user) {
      return new Response(
        JSON.stringify({ error: 'Invalid session' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    let message: string
    let history: any[] = []
    try {
      const body = await req.json()
      message = body.message
      history = body.history
    } catch {
      return new Response(
        JSON.stringify({ error: 'Invalid JSON body' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (!message || typeof message !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Missing message' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

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
        JSON.stringify({
          error: 'daily_limit_reached',
          limit: DAILY_MESSAGE_CAP,
          message: `You've reached your daily limit of ${DAILY_MESSAGE_CAP} messages. Your limit resets at midnight UTC.`
        }),
        { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const userContext = await fetchUserContext(adminClient, user.id)
    const systemPrompt = buildSystemPrompt(userContext)

    const messages = [
      { role: 'system', content: systemPrompt },
      ...(Array.isArray(history) ? history.slice(-6) : []),
      { role: 'user', content: message }
    ]

    const ollamaResponse = await fetch('https://ollama.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OLLAMA_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ model: OLLAMA_MODEL, messages, stream: false })
    })

    if (!ollamaResponse.ok) {
      const errText = await ollamaResponse.text()
      return new Response(
        JSON.stringify({ error: `Assistant unavailable: ${errText}` }),
        { status: 502, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
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
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (err: any) {
    console.error('Unhandled error:', err)
    return new Response(
      JSON.stringify({ error: 'Internal error', details: err.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
