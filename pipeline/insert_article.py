# THE INSERT ARTICLE FILE TAKES A NORMALIZED ARTICLE AND WRITES IT TO SUPABASE

from supabase_client import supabase

def insert_article(article):
  try:
    response = supabase.table("articles").insert({
      "title": article["title"],
      "content": article.get("content", ""),
      "url": article["url"],
      "source_id": article.get("source_id"),
      "source_type": "rss",
      "published_at": article["published_at"],
      "image_url": article.get("image_url", "")
    }).execute()

    return response.data[0]["id"]

  except Exception as e:
    print(f"Skipped article (likely duplicate): {article['url']}")
    return None


def insert_all(normalized_articles):
  articles_with_ids = []

  for article in normalized_articles:
    article_id = insert_article(article)
    if article_id is not None:
      articles_with_ids.append((article, article_id))

  return articles_with_ids
