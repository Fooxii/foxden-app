import './FeedSkeleton.css'

export default function FeedSkeleton() {
  return (
    <div className="feed-page-wrapper feed-page">
      <div className="skeleton-controls">
        <div className="skeleton-block skeleton-search" />
        <div className="skeleton-row">
          <div className="skeleton-block skeleton-pill" />
          <div className="skeleton-block skeleton-pill" />
          <div className="skeleton-block skeleton-pill" />
        </div>
      </div>
      <div className="card-grid">
        {Array.from({ length: 8 }).map((_, i) => (
          <div className="skeleton-card" key={i}>
            <div className="skeleton-block skeleton-img" />
            <div className="skeleton-block skeleton-line skeleton-title" />
            <div className="skeleton-block skeleton-line skeleton-title-short" />
            <div className="skeleton-footer-row">
              <div className="skeleton-block skeleton-tag" />
              <div className="skeleton-block skeleton-time" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
