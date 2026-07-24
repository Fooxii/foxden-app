import './TagList.css'

export default function TagList({ tags }) {
  if (!Array.isArray(tags) || tags.length === 0) return null

  const normalized = tags.map((tag) => {
    if (typeof tag === 'string') {
      return { key: tag, label: tag }
    }
    if (tag && typeof tag === 'object') {
      const key = tag.id ?? tag.tagId ?? JSON.stringify(tag)
      const label = tag.name ?? tag.tagName ?? tag.label ?? String(tag)
      return { key, label }
    }
    return { key: String(tag), label: String(tag) }
  })

  const uniqueTags = [...new Map(normalized.map((t) => [t.key, t])).values()]

  return (
    <div className="tag-list">
      {uniqueTags.map((tag) => (
        <span key={tag.key} className="tag-pill">
          {tag.label}
        </span>
      ))}
    </div>
  )
}
