# THE DUP_FILTER FILE WILL COMPARE INCOMING URLS WITH THOSE IN THE DATABASE, FILTERING OUT DUPLICATES
from supabase_client import supabase

def filter_duplicates(normalized):
  article_urls = supabase.table("articles").select("url").execute()
  existing_urls = {row["url"] for row in article_urls.data}

  filtered_entries = []
  for entry in normalized:
    if entry["url"] not in existing_urls:
      filtered_entries.append(entry)

  return filtered_entries
