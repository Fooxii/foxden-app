# THE TOPIC FILTER MATCHES ARTICLES TO RELEVANT TAGS USING A TWO-STEP APPROACH, EMBEDDINGS TO SHORTEN THE LIST OF CANDIDATES AND ZERO-SHOT CLASSIFICATION TO DETERMINE THE LINK

from supabase_client import supabase
from embedding_generator import generate_article_embedding
from relevance_classifier import (
  shortlist_candidates,
  rerank_candidates,
  rerank_score_all,
  keyword_match_articles,
  text_contains_any_keyword,
  classify_text_against_labels,
  classify_texts_against_label,
  build_classification_label,
  CUSTOM_TAG_RERANK_THRESHOLD
)

MAX_OFFICIAL_TAGS_PER_ARTICLE = 2
FETCH_BATCH_SIZE = 500


def fetch_all_tags():
  response = supabase.table("tags").select("id, name, embedding, is_official, keywords").execute()
  return [tag for tag in response.data if tag.get("embedding") or not tag.get("is_official")]


def fetch_all_articles_with_embeddings():
  articles = []
  offset = 0
  while True:
    response = (
      supabase.table("articles")
      .select("id, title, content, embedding")
      .range(offset, offset + FETCH_BATCH_SIZE - 1)
      .execute()
    )
    if not response.data:
      break
    articles.extend(response.data)
    offset += FETCH_BATCH_SIZE
  return [a for a in articles if a.get("embedding")]


def save_article_embedding(article_id, embedding):
  supabase.table("articles").update({"embedding": embedding}).eq("id", article_id).execute()


def get_official_tag_counts(article_ids):
  if not article_ids:
    return {}
  response = (
    supabase.table("article_tags")
    .select("article_id, tags!inner(is_official)")
    .in_("article_id", article_ids)
    .eq("tags.is_official", True)
    .execute()
  )
  counts = {}
  for row in response.data:
    counts[row["article_id"]] = counts.get(row["article_id"], 0) + 1
  return counts


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


def tag_label_text(tag):
  detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""
  return build_classification_label(tag["name"], tag.get("is_official", False), detail)


def article_text_of(article):
  return f"{article['title']}. {article.get('content', '')}"


def get_custom_tag_candidates(text, custom_tags):
  keyword_matched = {
    t["id"]: t for t in custom_tags
    if text_contains_any_keyword(text, (t.get("keywords") or [""])[0])
  }
  scored = rerank_score_all(text[:1000], custom_tags, tag_label_text)
  rerank_matched = {t["id"]: t for t, s in scored if s >= CUSTOM_TAG_RERANK_THRESHOLD}
  return list({**keyword_matched, **rerank_matched}.values())


def filter_article(article, article_id, all_tags):
  article_embedding = generate_article_embedding(article)
  if article_embedding is None:
    return []

  save_article_embedding(article_id, article_embedding)
  text = article_text_of(article)

  official_tags = [t for t in all_tags if t.get("is_official")]
  custom_tags = [t for t in all_tags if not t.get("is_official")]

  cosine_candidates = shortlist_candidates(article_embedding, official_tags)
  official_candidates = rerank_candidates(text[:1000], cosine_candidates, tag_label_text) if cosine_candidates else []
  custom_candidates = get_custom_tag_candidates(text, custom_tags)

  combined = official_candidates + custom_candidates
  if not combined:
    return []

  label_map = {t["name"]: tag_label_text(t) for t in combined}
  matches = classify_text_against_labels(text, label_map)

  name_to_tag = {t["name"]: t for t in combined}
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


def match_tag_against_existing_articles(tag_id, tag_name, tag_embedding, is_official=False, label_detail="", article_pool=None):
  articles = article_pool if article_pool is not None else fetch_all_articles_with_embeddings()

  classification_label = build_classification_label(tag_name, is_official, label_detail)

  if is_official:
    cosine_candidates = shortlist_candidates(tag_embedding, articles)
    candidate_ids = [a["id"] for a in cosine_candidates]
    tag_counts = get_official_tag_counts(candidate_ids)
    cosine_candidates = [
      a for a in cosine_candidates
      if tag_counts.get(a["id"], 0) < MAX_OFFICIAL_TAGS_PER_ARTICLE
    ]
    if not cosine_candidates:
      return 0
    candidates = rerank_candidates(classification_label, cosine_candidates, article_text_of)
  else:
    keyword_matched = {a["id"]: a for a in keyword_match_articles(label_detail, articles)}
    scored = rerank_score_all(classification_label, articles, article_text_of)
    rerank_matched = {a["id"]: a for a, s in scored if s >= CUSTOM_TAG_RERANK_THRESHOLD}
    candidates = list({**keyword_matched, **rerank_matched}.values())

  if not candidates:
    return 0

  texts = [article_text_of(a)[:1000] for a in candidates]
  scores = classify_texts_against_label(texts, classification_label)

  matches = 0
  for article, score in zip(candidates, scores):
    if score is not None:
      link_article_to_tag(article["id"], tag_id, score)
      matches += 1

  return matches
