# THE DUP_FILTER FILE WILL COMPARE INCOMING URLS WITH THOSE IN THE DATABASE, FILTERING OUT DUPLICATES

from supabase_client import supabase

BATCH_SIZE = 500


def get_all_existing_urls():
  urls = set()
  offset = 0
  while True:
    response = (
      supabase.table("articles")
      .select("url")
      .range(offset, offset + BATCH_SIZE - 1)
      .execute()
    )
    if not response.data:
      break
    urls.update(row["url"] for row in response.data)
    offset += BATCH_SIZE
  return urls


def filter_duplicates(normalized):
  existing_urls = get_all_existing_urls()
  return [entry for entry in normalized if entry["url"] not in existing_urls]
