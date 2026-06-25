# THE NORMALIZER FILE TAKES RAW ARTICLE DATA FROM THE FETCHER AND STANDARDIZES IT

from bs4 import BeautifulSoup
from fetcher import fetch_all_sources

# Returns only the paragraphs of the raw html
def clean_html(raw_html):
    # if there's no html at all, return an empty string instead of crashing
    if raw_html is None:
        return ""

    soup = BeautifulSoup(raw_html, 'html.parser')
    paragraphs = soup.find_all('p')
    clean_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
    return clean_text


def normalize_entry(entry):
    return {
        "source_guid": entry["guid"],
        "title": entry["title"],
        "author": entry["author"],
        "link": entry["link"],
        "thumbnail": entry["thumbnail"],
        "summary": clean_html(entry["raw_html"]),
        "published": entry["published"]
    }


def normalize_all(raw_entries):
    normalized = []
    for entry in raw_entries:
        normalized.append(normalize_entry(entry))
    return normalized

# -------------- FOR TESTING ------------------
if __name__ == "__main__":
    raw_entries = fetch_all_sources()
    normalized_entries = normalize_all(raw_entries)

    for article in normalized_entries:
        print(article["summary"], end="\n\n")
