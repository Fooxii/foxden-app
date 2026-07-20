# THE FEED BUILDER ASSEMBLES A RANKED, PERSONALIZED FEED FOR A GIVEN USER

from supabase_client import supabase
from datetime import datetime, timezone

RECENCY_WEIGHT = 0.7
RELEVANCE_WEIGHT = 0.3


def get_user_tags(user_id):
  response = supabase.table("user_tags").select("tag_id, tags(name)").eq("user_id", user_id).execute()
  return response.data


def get_articles_for_tags(tag_ids):
  if not tag_ids:
    return []

  response = (
    supabase.table("article_tags")
    .select("article_id, tag_id, similarity_score, articles(*)")
    .in_("tag_id", tag_ids)
    .execute()
  )
  return response.data


def calculate_recency_score(published_at):
  published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
  now = datetime.now(timezone.utc)
  hours_old = (now - published).total_seconds() / 3600

  if hours_old >= 48:
    return 0.0
  return 1 - (hours_old / 48)


def calculate_final_score(article_row):
  recency = calculate_recency_score(article_row["articles"]["published_at"])
  relevance = article_row.get("similarity_score") or 0.0

  return (recency * RECENCY_WEIGHT) + (relevance * RELEVANCE_WEIGHT)


def build_feed(user_id):
  user_tags = get_user_tags(user_id)
  tag_ids = [tag["tag_id"] for tag in user_tags]

  linked_articles = get_articles_for_tags(tag_ids)
  feed_by_tag = {}

  for row in linked_articles:
    tag_id = row["tag_id"]
    article = row["articles"]
    score = calculate_final_score(row)

    if tag_id not in feed_by_tag:
      feed_by_tag[tag_id] = []

    feed_by_tag[tag_id].append({
      "article": article,
      "score": round(score, 4)
    })

  for tag_id in feed_by_tag:
    feed_by_tag[tag_id].sort(key=lambda x: x["score"], reverse=True)

  return feed_by_tag
