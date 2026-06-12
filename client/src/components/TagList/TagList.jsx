export default function TagList({ tags }) {
  return(
    <div>
      {tags.map((tag) => (
        <span>{tag}</span>
      ))}
    </div>
  )
}
