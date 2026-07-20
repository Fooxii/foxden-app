# THE FETCHER FILE IS USED TO FETCH DATA FROM A LIST OF SOURCES
import feedparser
import calendar
from datetime import datetime, timezone
from supabase_client import supabase

def get_published_at(item):
  if item.get('published_parsed'):
    dt = datetime.fromtimestamp(calendar.timegm(item.published_parsed), tz=timezone.utc)
    return dt.isoformat()
  return item.get('published')


# fetches only rss sources from the sources table
def get_rss_sources():
  response = supabase.table("sources").select("id, url").eq("source_type", "rss").execute()
  return response.data


def fetch_all_sources():
  feed_all = []
  sources = get_rss_sources()

  for source in sources:
    feed = feedparser.parse(source["url"])

    for item in feed.entries:
      # finds html content, falls back to summary if missing
      raw_html = None
      if item.get('content'):
        for content_item in item.content:
          if content_item.get('type') == 'text/html':
            raw_html = content_item['value']
            break

      if raw_html is None:
        raw_html = item.get('summary', '')

      # defensively find a unique identifier
      if not item.get('id'):
        source_guid = item.link
      else:
        source_guid = item.id

      # defensively find a thumbnail, some sources won't have one
      if item.get('media_thumbnail'):
        image_url = item.media_thumbnail[0]['url']
      else:
        image_url = None

      entry = {
        "source_guid": source_guid,
        "title": item.title,
        "url": item.link,
        "image_url": image_url,
        "raw_html": raw_html,
        "published_at": get_published_at(item),
        "source_id": source["id"]
      }

      feed_all.append(entry)

  return feed_all
