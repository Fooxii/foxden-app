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
  SHORTLIST_COSINE_THRESHOLD,
  SHORTLIST_MAX_CANDIDATES,
  FINAL_MATCH_THRESHOLD,
)
from topic_filter import fetch_all_tags
from supabase_client import supabase

PER_SOURCE_SAMPLE = 2
UNLINKED_SAMPLE_SIZE = 10
NEAR_MISS_COUNT = 5


# ─────────────────────────── article sourcing ───────────────────────────

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
  response = supabase.table("articles").select("id, title, content, embedding").execute()
  return [a for a in response.data if a.get("embedding")]


def get_unlinked_articles(limit):
  linked_response = supabase.table("article_tags").select("article_id").execute()
  linked_ids = {row["article_id"] for row in linked_response.data}

  articles_response = (
    supabase.table("articles")
    .select("id, title, content, published_at, embedding")
    .execute()
  )

  unlinked = [a for a in articles_response.data if a["id"] not in linked_ids]
  return random.sample(unlinked, min(limit, len(unlinked)))


def get_article_embedding(article):
  if article.get("embedding"):
    return parse_embedding(article["embedding"])
  return generate_article_embedding(article)


# ─────────────────────── article → tags direction (tests 1 & 3) ───────────────────────

def rank_all_tags_by_cosine(article_embedding, tag_pool):
  scored = []
  for tag in tag_pool:
    emb = tag.get("embedding")
    if not emb:
      continue
    score = cosine_similarity(article_embedding, parse_embedding(emb))
    scored.append((tag, score))
  scored.sort(key=lambda x: x[1], reverse=True)
  return scored


def print_stage1_detail(tag_pool, article_embedding):
  ranked = rank_all_tags_by_cosine(article_embedding, tag_pool)
  passed = [(t, s) for t, s in ranked if s >= SHORTLIST_COSINE_THRESHOLD][:SHORTLIST_MAX_CANDIDATES]
  failed = [(t, s) for t, s in ranked if s < SHORTLIST_COSINE_THRESHOLD]

  print(f"STAGE 1 — shortlisted ({len(passed)}, threshold {SHORTLIST_COSINE_THRESHOLD}):")
  if not passed:
    print("  none")
  for tag, score in passed:
    print(f"  \u2713 {tag['name']:<24} {score:.4f}")

  if failed:
    print(f"STAGE 1 — closest misses (below {SHORTLIST_COSINE_THRESHOLD}):")
    for tag, score in failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {tag['name']:<24} {score:.4f}")

  return [t for t, _ in passed]


def print_stage2_detail(article, shortlist):
  if not shortlist:
    print("STAGE 2 — skipped, nothing passed stage 1\n")
    return

  text = f"{article['title']}. {article.get('content', '')}"

  label_map = {}
  for tag in shortlist:
    detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""
    label = build_classification_label(tag["name"], tag.get("is_official", False), detail)
    label_map[tag["name"]] = label
    if not tag.get("is_official"):
      print(f"  [custom label for '{tag['name']}': \"{label}\"]")

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
    print(f"STAGE 2 — closest misses (below {FINAL_MATCH_THRESHOLD}):")
    for name, score in failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {name:<24} {score:.4f}")
  print()


# ─────────────────────── tag → articles direction (test 2) ───────────────────────

def rank_articles_by_cosine_for_tag(tag_embedding, articles):
  scored = []
  for article in articles:
    emb = article.get("embedding")
    if not emb:
      continue
    score = cosine_similarity(tag_embedding, parse_embedding(emb))
    scored.append((article, score))
  scored.sort(key=lambda x: x[1], reverse=True)
  return scored


def print_stage1_detail_for_tag(tag_embedding, articles):
  ranked = rank_articles_by_cosine_for_tag(tag_embedding, articles)
  passed = [(a, s) for a, s in ranked if s >= SHORTLIST_COSINE_THRESHOLD][:SHORTLIST_MAX_CANDIDATES]
  failed = [(a, s) for a, s in ranked if s < SHORTLIST_COSINE_THRESHOLD]

  print(f"STAGE 1 — shortlisted ({len(passed)}, threshold {SHORTLIST_COSINE_THRESHOLD}):")
  if not passed:
    print("  none")
  for article, score in passed:
    print(f"  \u2713 {article['title'][:60]:<60} {score:.4f}")

  if failed:
    print(f"STAGE 1 — closest misses (below {SHORTLIST_COSINE_THRESHOLD}):")
    for article, score in failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {article['title'][:60]:<60} {score:.4f}")

  return [a for a, _ in passed]


def print_stage2_detail_for_tag(tag, shortlisted_articles):
  if not shortlisted_articles:
    print("STAGE 2 — skipped, nothing passed stage 1\n")
    return

  detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""
  label = build_classification_label(tag["name"], tag.get("is_official", False), detail)
  if not tag.get("is_official"):
    print(f"  [custom label used: \"{label}\"]")

  scored = []
  for article in shortlisted_articles:
    text = f"{article['title']}. {article.get('content', '')}"
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
    print(f"STAGE 2 — closest misses (below {FINAL_MATCH_THRESHOLD}):")
    for article, score in failed[:NEAR_MISS_COUNT]:
      print(f"  \u2717 {article['title'][:60]:<60} {score:.4f}")
  print()


# ──────────────────────────── the three tests ────────────────────────────

def run_test_sample_articles():
  print("\n=== TEST 1: Sample articles, matched against every tag ===\n")
  articles = get_sample_articles()
  all_tags = fetch_all_tags()
  print(f"{len(articles)} sample articles, {len(all_tags)} tags\n")

  for article in articles:
    print("=" * 80)
    print(f"TITLE: {article['title']}")
    embedding = generate_article_embedding(article)
    shortlist = print_stage1_detail(all_tags, embedding)
    print_stage2_detail(article, shortlist)


def run_test_custom_tags():
  print("\n=== TEST 2: A custom tag, ranked against every existing article ===\n")
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

  articles = get_all_articles_with_embeddings()
  print(f"\nSearching across {len(articles)} existing articles\n")

  for tag in tags_to_test:
    print("=" * 80)
    print(f"CUSTOM TAG: {tag['name']}")
    tag_embedding = parse_embedding(tag["embedding"])
    shortlist = print_stage1_detail_for_tag(tag_embedding, articles)
    print_stage2_detail_for_tag(tag, shortlist)


def run_test_unlinked_articles():
  print("\n=== TEST 3: Random sample of existing articles with zero tag links ===\n")
  articles = get_unlinked_articles(UNLINKED_SAMPLE_SIZE)

  if not articles:
    print("No unlinked articles found — everything currently has at least one tag.\n")
    return

  all_tags = fetch_all_tags()
  print(f"{len(articles)} unlinked articles (randomly sampled), {len(all_tags)} tags\n")

  for article in articles:
    print("=" * 80)
    print(f"TITLE: {article['title']}")
    embedding = get_article_embedding(article)
    shortlist = print_stage1_detail(all_tags, embedding)
    print_stage2_detail(article, shortlist)


# ─────────────────────────────── menu ───────────────────────────────

if __name__ == "__main__":
  print("Which test do you want to run?")
  print("  1. Sample articles      (fresh fetch, matched against every tag)")
  print("  2. Custom tags          (pick a tag, ranked against every existing article)")
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