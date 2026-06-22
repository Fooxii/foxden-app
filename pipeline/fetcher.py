#
# THE FETCHER FILE IS USED TO FETCH DATA FROM A LIST OF SOURCES
#

import feedparser
from bs4 import BeautifulSoup
# import source list from external file

# Temp source list for testing
source_list = ['https://www.pcgamer.com/feeds.xml']

# feed_all is list containing rss output of each source
feed_all = []

# for every source in the source list a feed is created
for source in source_list:
  feed = feedparser.parse(source)
  # for every entry in each of the feeds data will be saved for future use in the pipeline
  for item in feed.entries:
    raw_html = None
    for content_item in item.content:
      if content_item.get('type') == 'text/html':
        raw_html = content_item['value']
        break

    if raw_html is None:
      raw_html = item.summary
    # uses BeautifulSoup to parse the raw_html returned and only returns text inside p tags
    soup = BeautifulSoup(raw_html, 'html.parser')

    paragraphs = soup.find_all('p')
    clean_text = ' '.join(p.get_text(strip=True) for p in paragraphs)

    # ------------ FOR TESTING ------------------
    # print(item.title)
    # print(item.author)
    # print(item.link)
    # print(item.media_thumbnail[0]['url'])
    # print(clean_text)

    title = item.title
    author = item.author
    link = item.link
    thumbnail = item.media_thumbnail[0]['url']
