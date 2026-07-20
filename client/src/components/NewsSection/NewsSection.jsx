import NewsCard from "../NewsCard/NewsCard"
import { mockArticles } from '../../data/mockData.js'

export default function NewsSection() {
  return (
    <div className="news-section">
      {mockArticles.map((article) => (
        <NewsCard key={article.id} {...article} />
      ))}
    </div>
  )
}
