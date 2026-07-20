import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { buildFeed } from '../../services/feedService'
import { browseTags, followTag, unfollowTag } from '../../services/tagService'
import { useDragScroll } from '../../utils/useDragScroll'
import NewsCard from '../../components/NewsCard/NewsCard'
import ClusterCard from '../../components/ClusterCard/ClusterCard'
import ChatAssistant from '../../components/ChatAssistant/ChatAssistant'
import FeedSkeleton from '../../components/FeedSkeleton/FeedSkeleton'
import './FeedPage.css'

export default function FeedPage() {
  const { user } = useAuth()
  const [feed, setFeed] = useState(null)
  const [allTags, setAllTags] = useState([])
  const [pinnedTagId, setPinnedTagId] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [sortMode, setSortMode] = useState('relevance')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const hasLoadedRef = useRef(false)
  const dragScroll = useDragScroll()

  const load = async (silent = false) => {
    if (!user) return
    if (!hasLoadedRef.current) setLoading(true)
    else if (silent) setRefreshing(true)

    try {
      const [feedResult, tags] = await Promise.all([buildFeed(user.id), browseTags(user.id)])
      setFeed(feedResult)
      setAllTags(tags)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      setRefreshing(false)
      hasLoadedRef.current = true
    }
  }

  useEffect(() => {
    if (user && !hasLoadedRef.current) load()
  }, [user])

  const togglePin = (tagId) => setPinnedTagId((prev) => (prev === tagId ? null : tagId))

  const handleUnfollow = async (tagId, e) => {
    e.stopPropagation()
    await unfollowTag(user.id, tagId)
    if (pinnedTagId === tagId) setPinnedTagId(null)
    load(true)
  }

  const handleFollow = async (tagId) => {
    await followTag(user.id, tagId)
    load(true)
  }

  if (loading) return <FeedSkeleton />
  if (error) return <div className="feed-page-wrapper feed-page"><p className="feed-empty">{error}</p></div>

  const tags = feed?.tags || []
  const items = feed?.items || []
  const followedIds = new Set(tags.map((t) => t.tagId))

  const searchResults = allTags.filter((t) =>
    !followedIds.has(t.id) &&
    (searchTerm.trim() === '' || t.name.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  let visibleItems = pinnedTagId ? items.filter((item) => item.matchedTagIds.includes(pinnedTagId)) : items
  visibleItems = [...visibleItems].sort((a, b) =>
    sortMode === 'recency' ? new Date(b.published_at) - new Date(a.published_at) : b.score - a.score
  )

  return (
    <div className="feed-page-wrapper feed-page">
      <div className="feed-controls">
        <div className="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            type="text"
            placeholder="Click to browse topics you can follow..."
            value={searchTerm}
            onFocus={() => setIsSearchOpen(true)}
            onBlur={() => setIsSearchOpen(false)}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {isSearchOpen && searchResults.length > 0 && (
            <div className="search-results" onMouseDown={(e) => e.preventDefault()}>
              {searchResults.map((t) => (
                <button key={t.id} className="search-result-item" onClick={() => handleFollow(t.id)}>
                  <span>{!t.is_official && '★ '}{t.name}</span>
                  <span className="add-label">+ Follow</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="controls-row">
          {tags.length > 0 && (
            <div
              className="filter-bar"
              ref={dragScroll.ref}
              onMouseDown={dragScroll.onMouseDown}
              onMouseLeave={dragScroll.onMouseLeave}
              onMouseUp={dragScroll.onMouseUp}
              onMouseMove={dragScroll.onMouseMove}
            >
              {tags.map((t) => (
                <button key={t.tagId} className={`filter-pill ${pinnedTagId === t.tagId ? 'pinned' : ''}`} onClick={() => togglePin(t.tagId)}>
                  {t.tagName}
                  <span className="remove-tag" onClick={(e) => handleUnfollow(t.tagId, e)} title="Unfollow">×</span>
                </button>
              ))}
              {refreshing && <span className="refresh-indicator">Updating...</span>}
            </div>
          )}
          {tags.length > 0 && (
            <div className="sort-toggle">
              <button className={sortMode === 'relevance' ? 'active' : ''} onClick={() => setSortMode('relevance')}>Relevance</button>
              <button className={sortMode === 'recency' ? 'active' : ''} onClick={() => setSortMode('recency')}>Recency</button>
            </div>
          )}
        </div>
      </div>

      {tags.length === 0 && <p className="feed-empty">Your feed is empty. Click the search bar above to follow some topics.</p>}
      {tags.length > 0 && visibleItems.length === 0 && <p className="feed-empty">No articles yet for this topic — check back soon.</p>}

      {visibleItems.length > 0 && (
        <div className="card-grid">
          {visibleItems.map((item) => item.isCluster ? (
            <ClusterCard key={item.id} headline={item.headline} members={item.members} tags={item.matchedTagNames} />
          ) : (
            <NewsCard
              key={item.id}
              title={item.title}
              publishedAt={item.published_at}
              tags={item.matchedTagNames}
              url={item.url}
              imageUrl={item.image_url}
            />
          ))}
        </div>
      )}

      <ChatAssistant />
    </div>
  )
}
