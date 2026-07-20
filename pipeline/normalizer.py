# THE NORMALIZER FILE TAKES RAW ARTICLE DATA FROM THE FETCHER AND STANDARDIZES IT

from bs4 import BeautifulSoup
from fetcher import fetch_all_sources
from full_content_fetcher import get_article_content

def clean_html(raw_html):
  if raw_html is None:
    return ""

  soup = BeautifulSoup(raw_html, 'html.parser')
  paragraphs = soup.find_all('p')
  clean_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
  return clean_text


def normalize_entry(entry):
  fallback_content = clean_html(entry["raw_html"])
  full_content = get_article_content(entry["url"], fallback_content)

  return {
    "source_guid": entry["source_guid"],
    "title": entry["title"],
    "url": entry["url"],
    "image_url": entry["image_url"],
    "content": full_content,
    "published_at": entry["published_at"],
    "source_id": entry["source_id"]
  }


def normalize_all(raw_entries):
  normalized = []
  for entry in raw_entries:
    normalized.append(normalize_entry(entry))
  return normalized


if __name__ == "__main__":
  raw_entries = fetch_all_sources()
  normalized_entries = normalize_all(raw_entries)

  for article in normalized_entries:
    print(article)