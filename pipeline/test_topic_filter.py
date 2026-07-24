# TEST TOPIC FILTER IS USED TO TEST THE TOPIC FILTERING
#   1. Sample articles      — fresh fetch across sources, matched against every tag
#   2. Custom tags only     — fresh fetch across sources, matched against only custom tags
#   3. Unlinked articles    — existing articles in the db with zero tag links, matched against every tag, to see why they were missed

import random
from fetcher import fetch_all_sources
from normalizer import normalize_entry
from embedding_generator import generate_article_embedding
from relevance_classifier import (
  cosine_similarity,
  parse_embedding,
  build_classification_label,
  get_raw_classification_scores,
  text_contains_any_keyword,
  rerank_score_all,
  SHORTLIST_COSINE_THRESHOLD,
  SHORTLIST_MAX_CANDIDATES,
  CUSTOM_TAG_RERANK_THRESHOLD,
  FINAL_MATCH_THRESHOLD,
)
from topic_filter import fetch_all_tags, fetch_all_articles_with_embeddings
from supabase_client import supabase

PER_SOURCE_SAMPLE = 2
UNLINKED_SAMPLE_SIZE = 10
NEAR_MISS_COUNT = 5
BATCH_SIZE = 500


def get_sample_articles():
  raw = fetch_all_sources()
  by_source = {}
  for entry in raw:
    by_source.setdefault(entry["source_id"], []).append(entry)
  sampled_raw = []
  for entries in by_source.values():
    sampled_raw.extend(entries[:PER_SOURCE_SAMPLE])
  return [normalize_entry(entry) for entry in sampled_raw]


def get_all_articles_with_embeddings():
  articles = fetch_all_articles_with_embeddings()
  print(f"  ({len(articles)} articles with a saved embedding, fully paginated)")
  return articles


def get_linked_article_ids():
  ids = set()
  offset = 0
  while True:
    response = (
      supabase.table("article_tags")
      .select("article_id")
      .range(offset, offset + BATCH_SIZE - 1)
      .execute()
    )
    if not response.data:
      break
    ids.update(row["article_id"] for row in response.data)
    offset += BATCH_SIZE
  return ids


def get_all_articles_raw():
  articles = []
  offset = 0
  while True:
    response = (
      supabase.table("articles")
      .select("id, title, content, published_at, embedding")
      .range(offset, offset + BATCH_SIZE - 1)
      .execute()
    )
    if not response.data:
      break
    articles.extend(response.data)
    offset += BATCH_SIZE
  return articles


def get_unlinked_articles_full():
  linked_ids = get_linked_article_ids()
  articles = fetch_all_articles_with_embeddings()
  return [a for a in articles if a["id"] not in linked_ids]


def get_unlinked_sample(limit):
  linked_ids = get_linked_article_ids()
  articles = get_all_articles_raw()
  unlinked = [a for a in articles if a["id"] not in linked_ids]
  return random.sample(unlinked, min(limit, len(unlinked)))


def get_article_embedding(article):
  if article.get("embedding"):
    return parse_embedding(article["embedding"])
  return generate_article_embedding(article)


def tag_label_text(tag):
  detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""
  return build_classification_label(tag["name"], tag.get("is_official", False), detail)


def article_text_of(article):
  return f"{article['title']}. {article.get('content', '')}"


def preview_stage1_for_article(article_embedding, text, all_tags):
  official_tags = [t for t in all_tags if t.get("is_official")]
  custom_tags = [t for t in all_tags if not t.get("is_official")]

  scored = []
  for tag in official_tags:
    emb = tag.get("embedding")
    if not emb:
      continue
    score = cosine_similarity(article_embedding, parse_embedding(emb))
    scored.append((tag, score))
  scored.sort(key=lambda x: x[1], reverse=True)

  official_passed = [t for t, s in scored if s >= SHORTLIST_COSINE_THRESHOLD][:SHORTLIST_MAX_CANDIDATES]
  official_failed = [(t, s) for t, s in scored if s < SHORTLIST_COSINE_THRESHOLD]

  print(f"STAGE 1 (official, cosine) — shortlisted ({len(official_passed)}, threshold {SHORTLIST_COSINE_THRESHOLD}):")
  if not official_passed:
    print("  none")
  for tag, score in [(t, s) for t, s in scored if t in official_passed]:
    print(f"  \u2713 {tag['name']:<24} {score:.4f}")
  if official_failed:
    print(f"STAGE 1 (official) — closest misses:")
    for tag, score in official_failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {tag['name']:<24} {score:.4f}")

  keyword_hits = {t["id"] for t in custom_tags if text_contains_any_keyword(text, (t.get("keywords") or [""])[0])}
  rerank_scored = rerank_score_all(text[:1000], custom_tags, tag_label_text)
  rerank_hits = {t["id"]: s for t, s in rerank_scored if s >= CUSTOM_TAG_RERANK_THRESHOLD}

  print(f"STAGE 1 (custom, keyword OR cross-encoder \u2265 {CUSTOM_TAG_RERANK_THRESHOLD}):")
  custom_candidates = []
  for tag, score in rerank_scored:
    kw = tag["id"] in keyword_hits
    ce = tag["id"] in rerank_hits
    if kw or ce:
      custom_candidates.append(tag)
      via = "keyword+cross-encoder" if kw and ce else ("keyword only" if kw else "cross-encoder")
      print(f"  \u2713 {tag['name']:<24} {score:.4f}  [{via}]")
  if not custom_candidates:
    print("  none")

  return official_passed + custom_candidates


def print_stage2_for_article(article, candidates):
  if not candidates:
    print("STAGE 2 — skipped, nothing passed stage 1\n")
    return

  text = article_text_of(article)
  label_map = {t["name"]: tag_label_text(t) for t in candidates}

  for t in candidates:
    if not t.get("is_official"):
      print(f"  [custom label for '{t['name']}': \"{tag_label_text(t)}\"]")

  raw_scores = get_raw_classification_scores(text, label_map)
  ranked = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
  passed = [(n, s) for n, s in ranked if s >= FINAL_MATCH_THRESHOLD]
  failed = [(n, s) for n, s in ranked if s < FINAL_MATCH_THRESHOLD]

  print(f"STAGE 2 — final matches ({len(passed)}, threshold {FINAL_MATCH_THRESHOLD}):")
  if not passed:
    print("  none")
  for name, score in passed:
    print(f"  \u2713 {name:<24} {score:.4f}")
  if failed:
    print(f"STAGE 2 — closest misses:")
    for name, score in failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {name:<24} {score:.4f}")
  print()


def preview_stage1_for_tag(tag, articles):
  detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""

  if tag.get("is_official"):
    tag_embedding = parse_embedding(tag["embedding"])
    scored = []
    for article in articles:
      emb = article.get("embedding")
      if not emb:
        continue
      score = cosine_similarity(tag_embedding, parse_embedding(emb))
      scored.append((article, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    candidates = [a for a, s in scored if s >= SHORTLIST_COSINE_THRESHOLD][:SHORTLIST_MAX_CANDIDATES]
    print(f"STAGE 1 (official, cosine) — shortlisted ({len(candidates)}):")
    for article in candidates:
      print(f"  \u2713 {article['title'][:65]}")
    return candidates

  label = tag_label_text(tag)
  keyword_hits = {a["id"] for a in articles if text_contains_any_keyword(article_text_of(a), detail)}
  scored = rerank_score_all(label, articles, article_text_of)
  rerank_hits = {a["id"]: s for a, s in scored if s >= CUSTOM_TAG_RERANK_THRESHOLD}

  candidates = []
  print(f"STAGE 1 (custom, keyword OR cross-encoder \u2265 {CUSTOM_TAG_RERANK_THRESHOLD}) — checked {len(articles)} articles:")
  for article, score in scored:
    kw = article["id"] in keyword_hits
    ce = article["id"] in rerank_hits
    if kw or ce:
      candidates.append(article)
      via = "keyword+cross-encoder" if kw and ce else ("keyword only" if kw else "cross-encoder")
      print(f"  \u2713 {article['title'][:55]:<55} {score:.4f}  [{via}]")
  if not candidates:
    print("  none matched either signal")
  print(f"  ({len(candidates)} of {len(articles)} articles matched)")
  return candidates


def print_stage2_for_tag(tag, candidates):
  if not candidates:
    print("STAGE 2 — skipped, nothing passed stage 1\n")
    return

  label = tag_label_text(tag)
  if not tag.get("is_official"):
    print(f"  [custom label used: \"{label}\"]")

  scored = []
  for article in candidates:
    text = article_text_of(article)
    raw = get_raw_classification_scores(text, {tag["name"]: label})
    scored.append((article, raw.get(tag["name"], 0.0)))

  scored.sort(key=lambda x: x[1], reverse=True)
  passed = [(a, s) for a, s in scored if s >= FINAL_MATCH_THRESHOLD]
  failed = [(a, s) for a, s in scored if s < FINAL_MATCH_THRESHOLD]

  print(f"STAGE 2 — final matches ({len(passed)}, threshold {FINAL_MATCH_THRESHOLD}):")
  if not passed:
    print("  none")
  for article, score in passed:
    print(f"  \u2713 {article['title'][:60]:<60} {score:.4f}")
  if failed:
    print(f"STAGE 2 — closest misses:")
    for article, score in failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {article['title'][:60]:<60} {score:.4f}")
  print()


def run_test_sample_articles():
  print("\n=== TEST 1: Sample articles, matched against every tag ===\n")
  articles = get_sample_articles()
  all_tags = fetch_all_tags()
  print(f"{len(articles)} sample articles, {len(all_tags)} tags\n")
  for article in articles:
    print("=" * 90)
    print(f"TITLE: {article['title']}")
    embedding = generate_article_embedding(article)
    text = article_text_of(article)
    candidates = preview_stage1_for_article(embedding, text, all_tags)
    print_stage2_for_article(article, candidates)


def run_test_custom_tags():
  print("\n=== TEST 2: A custom tag, ranked against existing articles ===\n")
  all_tags = fetch_all_tags()
  custom_tags = [t for t in all_tags if not t.get("is_official")]

  if not custom_tags:
    print("No custom tags exist yet — nothing to test.\n")
    return

  print("Which custom tag do you want to test?")
  for i, tag in enumerate(custom_tags, start=1):
    print(f"  {i}. {tag['name']}")
  print("  0. Test all of them")

  choice = input("\nEnter a number: ").strip()

  if choice == "0":
    tags_to_test = custom_tags
  else:
    try:
      tags_to_test = [custom_tags[int(choice) - 1]]
    except (ValueError, IndexError):
      print("Invalid choice.")
      return

  print("\nTest against:")
  print("  1. All articles")
  print("  2. Only unlinked articles (nothing tagged at all yet)")
  scope_choice = input("Enter a number: ").strip()

  if scope_choice == "2":
    articles = get_unlinked_articles_full()
    print(f"\n{len(articles)} unlinked articles found\n")
  else:
    articles = get_all_articles_with_embeddings()
    print()

  for tag in tags_to_test:
    print("=" * 90)
    print(f"CUSTOM TAG: {tag['name']}")
    candidates = preview_stage1_for_tag(tag, articles)
    print_stage2_for_tag(tag, candidates)


def run_test_unlinked_articles():
  print("\n=== TEST 3: Random sample of existing articles with zero tag links ===\n")
  articles = get_unlinked_sample(UNLINKED_SAMPLE_SIZE)
  if not articles:
    print("No unlinked articles found — everything currently has at least one tag.\n")
    return
  all_tags = fetch_all_tags()
  print(f"{len(articles)} unlinked articles (randomly sampled), {len(all_tags)} tags\n")
  for article in articles:
    print("=" * 90)
    print(f"TITLE: {article['title']}")
    embedding = get_article_embedding(article)
    text = article_text_of(article)
    candidates = preview_stage1_for_article(embedding, text, all_tags)
    print_stage2_for_article(article, candidates)


if __name__ == "__main__":
  print("Which test do you want to run?")
  print("  1. Sample articles      (fresh fetch, matched against every tag)")
  print("  2. Custom tags          (pick a tag; test against all or only unlinked articles)")
  print("  3. Unlinked articles    (random sample of articles with zero tag links)")

  choice = input("\nEnter 1, 2, or 3: ").strip()

  if choice == "1":
    run_test_sample_articles()
  elif choice == "2":
    run_test_custom_tags()
  elif choice == "3":
    run_test_unlinked_articles()
  else:
    print("Invalid choice — please run again and enter 1, 2, or 3.")
