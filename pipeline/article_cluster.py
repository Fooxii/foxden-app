# THE ARTICLE CLUSTER FILE WILL GROUP ARTICLES WITH SAME TOPICS TOGETHER

from supabase_client import supabase
from embedding_generator import generate_article_embedding
import numpy as np
import json

SIMILARITY_THRESHOLD = 0.85


def cosine_similarity(vec_a, vec_b):
  a = np.array(vec_a)
  b = np.array(vec_b)
  return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_matching_cluster(article_embedding):
  response = supabase.table("story_clusters").select("id, embedding").execute()
  clusters = response.data

  best_match_id = None
  best_score = 0.0

  for cluster in clusters:
    if not cluster.get("embedding"):
      continue

    cluster_embedding = cluster["embedding"]

    if isinstance(cluster_embedding, str):
      cluster_embedding = json.loads(cluster_embedding)

    score = cosine_similarity(article_embedding, cluster_embedding)

    if score > best_score:
      best_score = score
      best_match_id = cluster["id"]

  if best_score >= SIMILARITY_THRESHOLD:
    return best_match_id

  return None


def create_cluster(article, article_embedding):
  response = supabase.table("story_clusters").insert({
    "headline": article["title"],
    "source_count": 1,
    "embedding": article_embedding
  }).execute()
  return response.data[0]["id"]


def add_to_cluster(cluster_id):
  response = supabase.table("story_clusters").select("source_count").eq("id", cluster_id).execute()
  current_count = response.data[0]["source_count"]

  supabase.table("story_clusters").update({
    "source_count": current_count + 1
  }).eq("id", cluster_id).execute()


def link_article_to_cluster(article_id, cluster_id):
  supabase.table("cluster_articles").insert({
    "article_id": article_id,
    "cluster_id": cluster_id
  }).execute()

  supabase.table("articles").update({
    "cluster_id": cluster_id
  }).eq("id", article_id).execute()


def cluster_article(article, article_id):
  article_embedding = generate_article_embedding(article)

  if article_embedding is None:
    return None

  matching_cluster_id = find_matching_cluster(article_embedding)

  if matching_cluster_id:
    add_to_cluster(matching_cluster_id)
    link_article_to_cluster(article_id, matching_cluster_id)
    return matching_cluster_id
  else:
    new_cluster_id = create_cluster(article, article_embedding)
    link_article_to_cluster(article_id, new_cluster_id)
    return new_cluster_id


def cluster_all(articles_with_ids):
  for article, article_id in articles_with_ids:
    cluster_article(article, article_id)
