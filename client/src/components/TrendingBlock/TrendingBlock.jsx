export default function TrendingBlock({ source, items }) {
  return (
    <div className='trendingblock'>
      <h3>{source}</h3>
      {items.map((item) => (
        <div key={item.rank} className='trending-item'>
          <span className='trending-rank'>{item.rank}</span>
          <div className='trending-text'>
            <p className='trending-topic'>{item.topic}</p>
            <p className='trending-title'>{item.title}</p>
            <p className='trending-meta'>{item.meta}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
