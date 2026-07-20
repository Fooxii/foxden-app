# THE TOPIC FILTER MATCHES ARTICLES TO RELEVANT TAGS USING A TWO-STEP APPROACH, EMBEDDINGS TO SHORTEN THE LIST OF CANDIDATES AND ZERO-SHOT CLASSIFICATION TO DETERMINE THE LINK

from supabase_client import supabase
from embedding_generator import generate_article_embedding
from relevance_classifier import (
  shortlist_candidates,
  classify_text_against_labels,
  classify_texts_against_label,
  build_classification_label
)

MAX_OFFICIAL_TAGS_PER_ARTICLE = 2


def fetch_all_tags():
  response = supabase.table("tags").select("id, name, embedding, is_official, keywords").execute()
  return [tag for tag in response.data if tag.get("embedding")]


def save_article_embedding(article_id, embedding):
  supabase.table("articles").update({"embedding": embedding}).eq("id", article_id).execute()


def get_official_tag_count(article_id):
  response = (
    supabase.table("article_tags")
    .select("id, tags!inner(is_official)")
    .eq("article_id", article_id)
    .eq("tags.is_official", True)
    .execute()
  )
  return len(response.data)


def link_article_to_tag(article_id, tag_id, score):
  existing = (
    supabase.table("article_tags")
    .select("id")
    .eq("article_id", article_id)
    .eq("tag_id", tag_id)
    .execute()
  )
  if existing.data:
    return

  supabase.table("article_tags").insert({
    "article_id": article_id,
    "tag_id": tag_id,
    "similarity_score": score
  }).execute()


def filter_article(article, article_id, all_tags):
  article_embedding = generate_article_embedding(article)
  if article_embedding is None:
    return []

  save_article_embedding(article_id, article_embedding)

  candidate_tags = shortlist_candidates(article_embedding, all_tags)
  if not candidate_tags:
    return []

  text = f"{article['title']}. {article.get('content', '')}"
  name_to_tag = {t["name"]: t for t in candidate_tags}

  label_map = {}
  for name, tag in name_to_tag.items():
    detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""
    label_map[name] = build_classification_label(name, tag.get("is_official", False), detail)

  matches = classify_text_against_labels(text, label_map)

  official_matches = []
  custom_matches = []
  for name, score in matches.items():
    tag = name_to_tag[name]
    entry = {"tag_id": tag["id"], "tag_name": name, "score": score}
    (official_matches if tag.get("is_official") else custom_matches).append(entry)

  official_matches.sort(key=lambda m: m["score"], reverse=True)
  official_matches = official_matches[:MAX_OFFICIAL_TAGS_PER_ARTICLE]

  matched_tags = official_matches + custom_matches
  for m in matched_tags:
    link_article_to_tag(article_id, m["tag_id"], m["score"])

  return matched_tags


def filter_all(articles_with_ids):
  all_tags = fetch_all_tags()
  results = []
  for article, article_id in articles_with_ids:
    matched = filter_article(article, article_id, all_tags)
    results.append({"article_id": article_id, "matched_tags": matched})
  return results


def match_tag_against_existing_articles(tag_id, tag_name, tag_embedding, is_official=False, label_detail=""):
  response = supabase.table("articles").select("id, title, content, embedding").execute()
  articles = [a for a in response.data if a.get("embedding")]

  candidate_articles = shortlist_candidates(tag_embedding, articles)

  if is_official:
    candidate_articles = [
      a for a in candidate_articles
      if get_official_tag_count(a["id"]) < MAX_OFFICIAL_TAGS_PER_ARTICLE
    ]

  if not candidate_articles:
    return 0

  classification_label = build_classification_label(tag_name, is_official, label_detail)
  texts = [f"{a['title']}. {a.get('content', '')}" for a in candidate_articles]

  scores = classify_texts_against_label(texts, classification_label)

  matches = 0
  for article, score in zip(candidate_articles, scores):
    if score is not None:
      link_article_to_tag(article["id"], tag_id, score)
      matches += 1

  return matches
