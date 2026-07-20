import { supabase } from '../supabase'

export async function getUserProfile(userId) {
  const { data, error } = await supabase.from('users').select('*').eq('id', userId).single()
  if (error) throw error
  return data
}

export async function deleteAccount(userId) {
  const { error: tagsError } = await supabase
  .from('tags')
  .delete()
  .eq('created_by', userId)
  if (tagsError) throw tagsError

  const { error: userTagsError } = await supabase
  .from('user_tags')
  .delete()
  .eq('user_id', userId)
  if (userTagsError) throw userTagsError

  const { error: savedError } = await supabase
  .from('saved_articles')
  .delete()
  .eq('user_id', userId)
  if (savedError) throw savedError

  const { error: profileError } = await supabase
  .from('users')
  .delete()
  .eq('id', userId)
  if (profileError) throw profileError

  const { data: { session } } = await supabase.auth.getSession()
  const { error: fnError } = await supabase.functions.invoke('delete-account', {
    headers: { Authorization: `Bearer ${session.access_token}` }
  })
  if (fnError) throw fnError
}
