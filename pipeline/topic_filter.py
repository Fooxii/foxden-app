# THE TOPIC FILTER MATCHES ARTICLES TO RELEVANT TAGS USING A TWO-STAGE APPROACH:
# CHEAP EMBEDDING SHORTLIST, THEN ACCURATE NLI CLASSIFICATION FOR THE FINAL CALL
# OFFICIAL TAGS ARE CAPPED PER ARTICLE; CUSTOM TAGS ARE NOT

from supabase_client import supabase
from embedding_generator import generate_article_embedding
from relevance_classifier import shortlist_candidates, classify_text_against_labels

MAX_OFFICIAL_TAGS_PER_ARTICLE = 2


def fetch_all_tags():
  response = supabase.table("tags").select("id, name, embedding, is_official").execute()
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
  matches = classify_text_against_labels(text, list(name_to_tag.keys()))

  official_matches = []
  custom_matches = []
  for name, score in matches.items():
    tag = name_to_tag[name]
    entry = {"tag_id": tag["id"], "tag_name": name, "score": score}
    (official_matches if tag.get("is_official") else custom_matches).append(entry)

  # cap official tags to the strongest N matches; custom tags are uncapped
  # since each one belongs to a single user's own personal feed
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


def match_tag_against_existing_articles(tag_id, tag_name, tag_embedding, is_official=False):
  response = supabase.table("articles").select("id, title, content, embedding").execute()
  articles = [a for a in response.data if a.get("embedding")]

  candidate_articles = shortlist_candidates(tag_embedding, articles)

  matches = 0
  for article in candidate_articles:
    if is_official and get_official_tag_count(article["id"]) >= MAX_OFFICIAL_TAGS_PER_ARTICLE:
      continue

    text = f"{article['title']}. {article.get('content', '')}"
    result = classify_text_against_labels(text, [tag_name])
    if tag_name in result:
      link_article_to_tag(article["id"], tag_id, result[tag_name])
      matches += 1

  return matches
