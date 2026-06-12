export default function NewsCard({ title, source, time, contentType, tags }) {
  return (
    <div className='newscard'>
      <h4>{source}</h4>
      <p>{time}</p>
      <h3>{title}</h3>
      {tags.map((tag) => (
        <p>{tag}</p>
      ))}
    </div>
  )
}
