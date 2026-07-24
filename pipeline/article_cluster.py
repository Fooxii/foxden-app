# THE ARTICLE CLUSTER FILE WILL GROUP ARTICLES WITH SAME TOPICS TOGETHER

from supabase_client import supabase
from embedding_generator import generate_article_embedding
import numpy as np
import json

SIMILARITY_THRESHOLD = 0.85
BATCH_SIZE = 500


def cosine_similarity(vec_a, vec_b):
  a = np.array(vec_a)
  b = np.array(vec_b)
  return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def fetch_all_clusters():
  clusters = []
  offset = 0
  while True:
    response = (
      supabase.table("story_clusters")
      .select("id, embedding, source_count")
      .range(offset, offset + BATCH_SIZE - 1)
      .execute()
    )
    if not response.data:
      break
    clusters.extend(response.data)
    offset += BATCH_SIZE
  return clusters


def find_matching_cluster(article_embedding, clusters_cache):
  best_match = None
  best_score = 0.0

  for cluster in clusters_cache:
    if not cluster.get("embedding"):
      continue

    cluster_embedding = cluster["embedding"]
    if isinstance(cluster_embedding, str):
      cluster_embedding = json.loads(cluster_embedding)

    score = cosine_similarity(article_embedding, cluster_embedding)
    if score > best_score:
      best_score = score
      best_match = cluster

  return best_match if best_score >= SIMILARITY_THRESHOLD else None


def create_cluster(article, article_embedding, clusters_cache):
  response = supabase.table("story_clusters").insert({
    "headline": article["title"],
    "source_count": 1,
    "embedding": article_embedding
  }).execute()

  new_cluster = response.data[0]
  clusters_cache.append(new_cluster)
  return new_cluster["id"]


def add_to_cluster(cluster, clusters_cache):
  new_count = cluster["source_count"] + 1
  supabase.table("story_clusters").update({"source_count": new_count}).eq("id", cluster["id"]).execute()
  cluster["source_count"] = new_count


def link_article_to_cluster(article_id, cluster_id):
  supabase.table("cluster_articles").insert({
    "article_id": article_id,
    "cluster_id": cluster_id
  }).execute()

  supabase.table("articles").update({"cluster_id": cluster_id}).eq("id", article_id).execute()


def cluster_article(article, article_id, clusters_cache):
  article_embedding = generate_article_embedding(article)
  if article_embedding is None:
    return None

  matching_cluster = find_matching_cluster(article_embedding, clusters_cache)

  if matching_cluster:
    add_to_cluster(matching_cluster, clusters_cache)
    link_article_to_cluster(article_id, matching_cluster["id"])
    return matching_cluster["id"]
  else:
    new_cluster_id = create_cluster(article, article_embedding, clusters_cache)
    link_article_to_cluster(article_id, new_cluster_id)
    return new_cluster_id


def cluster_all(articles_with_ids):
  clusters_cache = fetch_all_clusters()
  for article, article_id in articles_with_ids:
    cluster_article(article, article_id, clusters_cache)
