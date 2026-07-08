# THE TOPIC FILTER MATCHES ARTICLES TO RELEVANT TAGS USING COSINE SIMILARITY

from supabase_client import supabase
from embedding_generator import generate_article_embedding
import numpy as np
import json

SIMILARITY_THRESHOLD = 0.40


def cosine_similarity(vec_a, vec_b):
  a = np.array(vec_a)
  b = np.array(vec_b)
  return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def fetch_all_tags():
  response = supabase.table("tags").select("id, name, embedding").execute()
  return [tag for tag in response.data if tag.get("embedding")]


def find_matching_tags(article_embedding, all_tags):
  matching_tags = []

  for tag in all_tags:
    tag_embedding = tag["embedding"]

    if isinstance(tag_embedding, str):
      tag_embedding = json.loads(tag_embedding)

    score = cosine_similarity(article_embedding, tag_embedding)
    if score >= SIMILARITY_THRESHOLD:
      matching_tags.append({
        "tag_id": tag["id"],
        "tag_name": tag["name"],
        "score": round(score, 4)
      })

  return matching_tags


def link_article_to_tags(article_id, matching_tags):
  for tag in matching_tags:
    supabase.table("article_tags").insert({
      "article_id": article_id,
      "tag_id": tag["tag_id"],
      "similarity_score": tag["score"]
    }).execute()


def filter_article(article, article_id, all_tags):
  article_embedding = generate_article_embedding(article)

  if article_embedding is None:
    return []

  matching_tags = find_matching_tags(article_embedding, all_tags)

  if matching_tags:
    link_article_to_tags(article_id, matching_tags)

  return matching_tags


def filter_all(articles_with_ids):
  all_tags = fetch_all_tags()

  results = []
  for article, article_id in articles_with_ids:
    matched = filter_article(article, article_id, all_tags)
    results.append({
      "article_id": article_id,
      "matched_tags": matched
    })

  return results
