import { supabase } from '../supabase'

export async function getUserFollowedTags(userId) {
  const { data, error } = await supabase
    .from('user_tags')
    .select('tag_id, tags(id, name, is_official)')
    .eq('user_id', userId)
  if (error) throw error
  return data.map((row) => row.tags).filter(Boolean)
}

export async function getUserCreatedTags(userId) {
  const { data, error } = await supabase
  .from('tags')
  .select('id, name')
  .eq('created_by', userId)
  .order('name')
  if (error) throw error
  return data
}

export async function browseTags(userId) {
  const { data, error } = await supabase
    .from('tags')
    .select('id, name, is_official, created_by')
    .or(`is_official.eq.true,created_by.eq.${userId}`)
    .order('name')
  if (error) throw error
  return data
}

export async function followTag(userId, tagId) {
  const { error } = await supabase
  .from('user_tags')
  .insert({ user_id: userId, tag_id: tagId })
  if (error) throw error
}

export async function unfollowTag(userId, tagId) {
  const { error } = await supabase
  .from('user_tags')
  .delete()
  .eq('user_id', userId)
  .eq('tag_id', tagId)
  if (error) throw error
}

export async function deleteCustomTag(tagId, userId) {
  const { error } = await supabase
  .from('tags')
  .delete()
  .eq('id', tagId)
  .eq('created_by', userId)
  if (error) throw error
}

export async function createCustomTag(userId, name, interestDescription) {
  const trimmedName = name.trim()

  const { data: existing } = await supabase
    .from('tags')
    .select('id')
    .eq('created_by', userId)
    .eq('is_official', false)
    .ilike('name', trimmedName)
    .maybeSingle()

  if (existing) {
    throw new Error(`You already have a custom tag called "${trimmedName}".`)
  }

  const { data: tag, error } = await supabase
    .from('tags')
    .insert({ name: trimmedName, keywords: [interestDescription], is_official: false, created_by: userId, embedding: null })
    .select()
    .single()

  if (error) {
    if (error.code === '23505') {
      throw new Error(`You already have a custom tag called "${trimmedName}".`)
    }
    if (error.message?.includes('maximum')) {
      throw new Error(error.message)
    }
    throw error
  }

  await followTag(userId, tag.id)
  return tag
}