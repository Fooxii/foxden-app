# THE SCHEDULER RUNS THE FULL PIPELINE ON A REPEATING INTERVAL

from apscheduler.schedulers.blocking import BlockingScheduler
from fetcher import fetch_all_sources
from normalizer import normalize_all
from dup_filter import filter_duplicates
from insert_article import insert_all
from article_cluster import cluster_all
from topic_filter import filter_all


def run_pipeline():
  print("Pipeline run started")

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


scheduler = BlockingScheduler()
scheduler.add_job(run_pipeline, 'interval', minutes=30)

if __name__ == "__main__":
  print("Scheduler starting — pipeline will run every 30 minutes")
  run_pipeline()
  scheduler.start()
