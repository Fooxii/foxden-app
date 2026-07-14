# FINDS TAGS WITH NO EMBEDDING YET (CREATED DIRECTLY FROM THE FRONTEND),
# GENERATES THE EMBEDDING, AND BACKFILLS MATCHES AGAINST EXISTING ARTICLES

from supabase_client import supabase
from tag_creation import enrich_tag_locally
from embedding_generator import generate_tag_embedding
from topic_filter import match_tag_against_existing_articles


def get_pending_tags():
  response = supabase.table("tags").select("id, name, keywords, is_official").is_("embedding", "null").execute()
  return response.data


def process_pending_tag(tag):
  interest_description = tag["keywords"][0] if tag.get("keywords") else ""
  text = interest_description if tag.get("is_official") else enrich_tag_locally(tag["name"], interest_description)

  embedding = generate_tag_embedding({"name": tag["name"], "keywords": [text]})
  supabase.table("tags").update({"embedding": embedding}).eq("id", tag["id"]).execute()

  return match_tag_against_existing_articles(
    tag["id"], tag["name"], embedding, is_official=tag.get("is_official", False)
  )


def process_all_pending_tags():
  pending = get_pending_tags()
  total_matches = 0

  for tag in pending:
    matches = process_pending_tag(tag)
    print(f"  Tag '{tag['name']}' embedded — matched {matches} existing articles")
    total_matches += matches

  return len(pending), total_matches
