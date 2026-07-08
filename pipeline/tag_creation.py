# THE TAG CREATION FILE HANDLES CREATING NEW CUSTOM TAGS FOR USERS

from supabase_client import supabase
from embedding_generator import generate_tag_embedding


def enrich_tag_locally(name, interest_description):
  return (
    f"{name} news and articles related to {interest_description}. "
    f"Covers updates, releases, reviews, and discussions about {name} "
    f"specifically involving {interest_description}."
  )


def create_custom_tag(user_id, name, interest_description):
  enriched_text = enrich_tag_locally(name, interest_description)

  embedding = generate_tag_embedding({
    "name": name,
    "keywords": [enriched_text]
  })

  response = supabase.table("tags").insert({
    "name": name,
    "keywords": [interest_description],
    "is_official": False,
    "created_by": user_id,
    "embedding": embedding
  }).execute()

  return response.data[0]["id"]


def follow_tag(user_id, tag_id):
  supabase.table("user_tags").insert({
    "user_id": user_id,
    "tag_id": tag_id
  }).execute()


def create_and_follow_tag(user_id, name, interest_description):
  tag_id = create_custom_tag(user_id, name, interest_description)
  follow_tag(user_id, tag_id)
  return tag_id
