import { useState } from 'react'
import { formatRelativeTime } from '../../utils/time'
import './ClusterCard.css'

export default function ClusterCard({ headline, members, tags }) {
  const [expanded, setExpanded] = useState(false)
  const thumb = members.find((m) => m.image_url)?.image_url

  return (
    <div className={`newscard cluster-card ${expanded ? 'expanded' : ''}`} onClick={() => setExpanded((e) => !e)}>
      <div className="newscard-img" style={thumb ? { backgroundImage: `url(${thumb})` } : undefined}>
        {!thumb && <span className="img-fallback">FoxDen</span>}
        <span className="cluster-badge">
          {members.length} sources
          <svg className="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </span>
      </div>

      <div className="newscard-body">
        <h3 className="newscard-title">{headline}</h3>
        <div className="newscard-footer">
          <div className="tag-list">{tags.map((t) => <span key={t} className="tag-pill">{t}</span>)}</div>
        </div>
      </div>

      <div className="cluster-dropdown" style={{ maxHeight: expanded ? '260px' : '0px' }}>
        <div className="cluster-dropdown-inner">
          {members.map((article) => (
            <a key={article.id} href={article.url} target="_blank" rel="noreferrer" className="cluster-member" onClick={(e) => e.stopPropagation()}>
              {article.image_url && <div className="member-img" style={{ backgroundImage: `url(${article.image_url})` }} />}
              <div className="member-body">
                <p className="member-title">{article.title}</p>
                <div className="member-meta">
                  <span className="member-source">{article.sources?.name || 'Unknown source'}</span>
                  <span className="member-date">{formatRelativeTime(article.published_at)}</span>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
