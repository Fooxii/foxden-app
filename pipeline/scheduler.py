from apscheduler.schedulers.blocking import BlockingScheduler
from fetcher import fetch_all_sources
from normalizer import normalize_all
from dup_filter import filter_duplicates
from insert_article import insert_all
from article_cluster import cluster_all
from topic_filter import filter_all
from pending_tag_processor import process_all_pending_tags


def run_pipeline():
  print("Pipeline run started")

  pending_count, backfill_matches = process_all_pending_tags()
  if pending_count:
    print(f"Processed {pending_count} pending tags, backfilled {backfill_matches} matches")

  raw = fetch_all_sources()
  print(f"Fetched: {len(raw)} raw articles")

  filtered_raw = filter_duplicates(raw)
  print(f"After dedup: {len(filtered_raw)} new articles")

  normalized = normalize_all(filtered_raw)
  print(f"Normalized: {len(normalized)} articles")

  articles_with_ids = insert_all(normalized)
  print(f"Inserted: {len(articles_with_ids)} articles")

  cluster_all(articles_with_ids)
  print("Clustering complete")

  filter_all(articles_with_ids)
  print("Topic matching complete")

  print("Pipeline run finished")


def check_pending_tags():
  count, matches = process_all_pending_tags()
  if count:
    print(f"[pending tags] processed {count}, backfilled {matches} matches")


scheduler = BlockingScheduler()
scheduler.add_job(run_pipeline, 'interval', minutes=15)
scheduler.add_job(check_pending_tags, 'interval', seconds=20)

if __name__ == "__main__":
  print("Scheduler starting — full pipeline every 15 minutes, pending tags every 20 seconds")
  run_pipeline()
  scheduler.start()
