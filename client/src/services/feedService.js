import { supabase } from '../supabase'

const RECENCY_WEIGHT = 0.7
const RELEVANCE_WEIGHT = 0.3
const CHUNK_SIZE = 100

function calculateRecencyScore(publishedAt) {
  const hoursOld = (new Date() - new Date(publishedAt)) / (1000 * 60 * 60)
  if (hoursOld >= 48) return 0
  return 1 - hoursOld / 48
}

function calculateCombinedScore(publishedAt, similarityScore) {
  return calculateRecencyScore(publishedAt) * RECENCY_WEIGHT + (similarityScore || 0) * RELEVANCE_WEIGHT
}

function chunk(arr, size) {
  const out = []
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size))
  return out
}

export async function getUserTags(userId) {
  const { data, error } = await supabase.from('user_tags').select('tag_id, tags(id, name)').eq('user_id', userId)
  if (error) throw error
  return [...new Map(data.map((t) => [t.tag_id, t])).values()]
}

export async function getArticlesForTags(tagIds) {
  if (!tagIds?.length) return []
  const { data, error } = await supabase
    .from('article_tags')
    .select('article_id, tag_id, similarity_score, articles(*, sources(name))')
    .in('tag_id', tagIds)
  if (error) throw error
  return [...new Map(data.map((r) => [`${r.article_id}-${r.tag_id}`, r])).values()]
}

async function getClusterMembers(clusterIds) {
  if (!clusterIds.length) return {}

  const map = {}
  for (const batch of chunk(clusterIds, CHUNK_SIZE)) {
    const { data, error } = await supabase
      .from('cluster_articles')
      .select('cluster_id, articles(*, sources(name))')
      .in('cluster_id', batch)
    if (error) throw error

    data.forEach((row) => {
      if (!map[row.cluster_id]) map[row.cluster_id] = []
      if (row.articles && !map[row.cluster_id].some((a) => a.id === row.articles.id)) {
        map[row.cluster_id].push(row.articles)
      }
    })
  }
  return map
}

async function getClusterHeadlines(clusterIds) {
  if (!clusterIds.length) return {}

  const map = {}
  for (const batch of chunk(clusterIds, CHUNK_SIZE)) {
    const { data, error } = await supabase
      .from('story_clusters')
      .select('id, headline')
      .in('id', batch)
    if (error) throw error
    data.forEach((row) => {
      map[row.id] = row.headline
    })
  }
  return map
}

export async function buildFeed(userId) {
  const userTags = await getUserTags(userId)
  const tagIds = userTags.map((t) => t.tag_id)
  const linkedArticles = await getArticlesForTags(tagIds)

  const clusterIds = [...new Set(
    linkedArticles.map((r) => r.articles.cluster_id).filter(Boolean)
  )]

  const [clusterMembersMap, clusterHeadlineMap] = await Promise.all([
    getClusterMembers(clusterIds),
    getClusterHeadlines(clusterIds),
  ])

  const itemsByKey = new Map()

  for (const row of linkedArticles) {
    const tagId = row.tag_id
    const tagName = userTags.find((t) => t.tag_id === tagId)?.tags?.name || 'Unknown'
    const clusterId = row.articles.cluster_id
    const score = calculateCombinedScore(row.articles.published_at, row.similarity_score)

    let key, entry

    if (clusterId) {
      const members = clusterMembersMap[clusterId] || [row.articles]

      if (members.length === 1) {
        key = `article-${members[0].id}`
        entry = { isCluster: false, id: members[0].id, ...members[0], score }
      } else {
        key = `cluster-${clusterId}`
        const newest = [...members].sort((a, b) => new Date(b.published_at) - new Date(a.published_at))[0]
        entry = {
          isCluster: true,
          id: key,
          headline: clusterHeadlineMap[clusterId] || newest.title,
          members,
          published_at: newest.published_at,
          score,
        }
      }
    } else {
      key = `article-${row.article_id}`
      entry = { isCluster: false, id: row.article_id, ...row.articles, score }
    }

    if (itemsByKey.has(key)) {
      const existing = itemsByKey.get(key)
      existing.matchedTagIds.add(tagId)
      existing.matchedTagNames.add(tagName)
      existing.score = Math.max(existing.score, score)
    } else {
      entry.matchedTagIds = new Set([tagId])
      entry.matchedTagNames = new Set([tagName])
      itemsByKey.set(key, entry)
    }
  }

  return {
    tags: userTags.map((t) => ({ tagId: t.tag_id, tagName: t.tags?.name })).filter((t) => t.tagName),
    items: [...itemsByKey.values()].map((item) => ({
      ...item,
      matchedTagIds: [...item.matchedTagIds],
      matchedTagNames: [...item.matchedTagNames],
    })),
  }
}
