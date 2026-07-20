import './TagList.css'

export default function TagList({ tags }) {
  return (
    <div className="tag-list">
      {tags.map((tag) => (
        <span key={tag} className="tag-pill">{tag}</span>
      ))}
    </div>
  )
}
