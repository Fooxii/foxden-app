# THIS TEST FILE PULLS A SMALL SAMPLE OF REAL ARTICLES ACROSS DIFFERENT SOURCES
# AND PRINTS THEIR FULL SIMILARITY SCORE AGAINST EVERY TAG, SORTED HIGH TO LOW
# THIS HELPS DIAGNOSE WHETHER THE PROBLEM IS THE THRESHOLD OR THE EMBEDDINGS THEMSELVES

from fetcher import fetch_all_sources
from normalizer import normalize_entry
from embedding_generator import generate_article_embedding
from topic_filter import fetch_all_tags, cosine_similarity
import json

# how many articles to sample PER SOURCE
PER_SOURCE_SAMPLE = 2


def get_sample_articles():
  raw = fetch_all_sources()

  # group raw entries by source so we can sample evenly across all of them
  by_source = {}
  for entry in raw:
    source_id = entry["source_id"]
    by_source.setdefault(source_id, []).append(entry)

  sampled_raw = []
  for source_id, entries in by_source.items():
    sampled_raw.extend(entries[:PER_SOURCE_SAMPLE])

  # only normalize the sampled entries, not the entire fetched batch
  # this avoids scraping full page content for articles we won't even test
  normalized = [normalize_entry(entry) for entry in sampled_raw]
  return normalized


def score_article_against_all_tags(article, all_tags):
  embedding = generate_article_embedding(article)

  if embedding is None:
    return []

  scored = []
  for tag in all_tags:
    tag_embedding = tag["embedding"]

    if isinstance(tag_embedding, str):
      tag_embedding = json.loads(tag_embedding)

    score = cosine_similarity(embedding, tag_embedding)
    scored.append((tag["name"], round(score, 4)))

  scored.sort(key=lambda x: x[1], reverse=True)
  return scored


def run_test():
  print("Fetching sample articles across sources...")
  articles = get_sample_articles()
  print(f"Got {len(articles)} sample articles\n")

  print("Fetching all tags...")
  all_tags = fetch_all_tags()
  print(f"Got {len(all_tags)} tags\n")

  for article in articles:
    print("=" * 80)
    print(f"TITLE: {article['title']}")
    print(f"CONTENT LENGTH: {len(article.get('content', ''))} characters")
    print(f"CONTENT PREVIEW: {article.get('content', '')[:150]}...")
    print("-" * 80)

    scores = score_article_against_all_tags(article, all_tags)

    for tag_name, score in scores:
      print(f"  {tag_name:<20} {score}")

    print()


if __name__ == "__main__":
  run_test()
