import TagList from '../TagList/TagList'
import { formatRelativeTime } from '../../utils/time'
import './NewsCard.css'

export default function NewsCard({ title, publishedAt, tags, url, imageUrl }) {
  return (
    <a className="newscard" href={url} target="_blank" rel="noreferrer">
      <div className="newscard-img" style={imageUrl ? { backgroundImage: `url(${imageUrl})` } : undefined}>
        {!imageUrl && <span className="img-fallback">FoxDen</span>}
      </div>
      <div className="newscard-body">
        <h3 className="newscard-title">{title}</h3>
        <TagList tags={tags} />
        <div className="newscard-footer">
          <span className="newscard-time">{formatRelativeTime(publishedAt)}</span>
        </div>
      </div>
    </a>
  )
}
