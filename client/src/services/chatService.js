import { supabase } from '../supabase'

export async function sendChatMessage(message, history) {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('You must be logged in to use the assistant.')

  const { data, error } = await supabase.functions.invoke('chat-assistant', {
    headers: { Authorization: `Bearer ${session.access_token}` },
    body: { message, history }
  })

  if (error) {
    throw new Error(error.context?.error || error.message || 'Something went wrong.')
  }

  return data
}
