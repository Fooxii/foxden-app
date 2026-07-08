# THE FULL CONTENT FETCHER FILE FETCHES ARTICLE CONTENT USING URL

import trafilatura


def fetch_full_text(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        return None
    return trafilatura.extract(downloaded)


def get_article_content(url, fallback_summary):
    full_text = fetch_full_text(url)

    if full_text is None or len(full_text) < 200:
        return fallback_summary  # falls back to RSS summary if scraping fails

    return full_text