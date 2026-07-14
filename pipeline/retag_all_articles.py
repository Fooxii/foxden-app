# ONE-TIME SCRIPT: wipes existing article-tag links and re-runs every
# article through the current two-stage (embedding shortlist + NLI
# classification) tagging system. Run manually, not from the scheduler.

from supabase_client import supabase
from topic_filter import fetch_all_tags, filter_article

BATCH_SIZE = 50


def clear_existing_links():
  print("Clearing existing article_tags links...")
  supabase.table("article_tags").delete().neq("article_id", "00000000-0000-0000-0000-000000000000").execute()
  print("Cleared.\n")


def get_all_articles():
  articles = []
  offset = 0
  while True:
    response = (
      supabase.table("articles")
      .select("id, title, content")
      .range(offset, offset + BATCH_SIZE - 1)
      .execute()
    )
    if not response.data:
      break
    articles.extend(response.data)
    offset += BATCH_SIZE
  return articles


def run():
  clear_existing_links()

  all_tags = fetch_all_tags()
  print(f"Loaded {len(all_tags)} tags\n")

  articles = get_all_articles()
  print(f"Re-tagging {len(articles)} articles...\n")

  for i, article in enumerate(articles, start=1):
    matched = filter_article(article, article["id"], all_tags)
    tag_names = [m["tag_name"] for m in matched]
    print(f"[{i}/{len(articles)}] {article['title'][:60]}  ->  {tag_names}")

  print("\nDone.")


if __name__ == "__main__":
  run()