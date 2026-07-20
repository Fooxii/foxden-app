import { supabase } from '../supabase'

export async function sendChatMessage(message, history) {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('You must be logged in to use the assistant.')

  const { data, error } = await supabase.functions.invoke('chat-assistant', {
    headers: { Authorization: `Bearer ${session.access_token}` },
    body: { message, history }
  })

  if (error) {
    let status = null
    let body = null

    try {
      status = error.status || error.context?.status || error.context?.code || null
      const raw = error.context?.body || error.context?.text || null
      body = typeof raw === 'string' ? JSON.parse(raw) : raw
    } catch {
      body = null
    }

    if (status === 429 || body?.error === 'daily_limit_reached') {
      return {
        reply: null,
        remaining: 0,
        limitReached: true,
        limit: body?.limit || 5,
        resetMessage: body?.message || `You've reached your daily limit of 5 messages. Come back tomorrow!`
      }
    }

    throw new Error(body?.message || body?.error || error.context?.error || error.message || 'Something went wrong.')
  }

  return data
}
