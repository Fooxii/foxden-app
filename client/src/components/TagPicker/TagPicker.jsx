import './TagPicker.css'

export default function TagPicker({ allTags, followedTagIds, onToggle }) {
  return (
    <div className="tag-picker">
      {allTags.map((tag) => {
        const isFollowed = followedTagIds.has(tag.id)
        return (
          <button
            key={tag.id}
            className={`tag-picker-pill ${isFollowed ? 'active' : ''}`}
            onClick={() => onToggle(tag.id, isFollowed)}
          >
            {!tag.is_official && '⭐ '}
            {tag.name}
          </button>
        )
      })}
    </div>
  )
}
