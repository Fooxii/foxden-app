# TEST TOPIC FILTER IS USED TO TEST THE TOPIC FILTERING

from fetcher import fetch_all_sources
from normalizer import normalize_entry
from embedding_generator import generate_article_embedding
from relevance_classifier import shortlist_candidates, classify_text_against_labels, build_classification_label
from topic_filter import fetch_all_tags

PER_SOURCE_SAMPLE = 2


def get_sample_articles():
  raw = fetch_all_sources()
  by_source = {}
  for entry in raw:
    by_source.setdefault(entry["source_id"], []).append(entry)

  sampled_raw = []
  for entries in by_source.values():
    sampled_raw.extend(entries[:PER_SOURCE_SAMPLE])

  return [normalize_entry(entry) for entry in sampled_raw]


def run_test():
  print("Fetching sample articles across sources...")
  articles = get_sample_articles()
  print(f"Got {len(articles)} sample articles\n")

  all_tags = fetch_all_tags()
  print(f"Got {len(all_tags)} tags\n")

  for article in articles:
    print("=" * 80)
    print(f"TITLE: {article['title']}")

    embedding = generate_article_embedding(article)
    shortlist = shortlist_candidates(embedding, all_tags)
    print(f"STAGE 1 shortlist ({len(shortlist)}): {[t['name'] for t in shortlist]}")

    if not shortlist:
      print("  no candidates passed the shortlist\n")
      continue

    text = f"{article['title']}. {article.get('content', '')}"

    label_map = {}
    for tag in shortlist:
      detail = (tag.get("keywords") or [""])[0] if not tag.get("is_official") else ""
      label_map[tag["name"]] = build_classification_label(tag["name"], tag.get("is_official", False), detail)

    print("STAGE 2 labels used:")
    for name, label in label_map.items():
      print(f"  {name:<20} -> \"{label}\"")

    final_matches = classify_text_against_labels(text, label_map)

    print("STAGE 2 final matches:")
    if not final_matches:
      print("  none passed the final threshold")
    else:
      for name, score in sorted(final_matches.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name:<20} {score}")
    print()


if __name__ == "__main__":
  run_test()
