import NewsCard from "../NewsCard/NewsCard"
import { mockArticles } from '../../data/mockData.js'

export default function NewsSection() {
  return (
    <div>
      {mockArticles.map((article) => (
        <NewsCard  
          key={article.id}
          title={article.title}
          source={article.source}
          time={article.time}
          contentType={article.contentType}
          tags={article.tags}
        />
      ))}
    </div>
  )
}
