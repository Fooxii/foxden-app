# THE FETCHER FILE IS USED TO FETCH DATA FROM A LIST OF SOURCES
import feedparser
#+import source list from external file

#-Temp source list for testing
source_list = ['https://www.pcgamer.com/feeds.xml']
def fetch_all_sources():
  # list containing rss output of each source
  feed_all = []

  # iterates through each source
  for source in source_list:
    # feed is the entire xml page
    feed = feedparser.parse(source)
    # iterates through each article
    for item in feed.entries:
      raw_html = None
      for content_item in item.content:
        if content_item.get('type') == 'text/html':
          raw_html = content_item['value']
          if not item.get('id'):
              source_guid = item.link
          else:
              source_guid = item.id
          title = item.title
          author = item.author
          link = item.link
          thumbnail = item.media_thumbnail[0]['url']
          published = item.published

          entry = {
            "source_guid": source_guid,
            "title": title,
            "author": author,
            "link": link,
            "thumbnail": thumbnail,
            "raw_html": raw_html,
            "published": published
          }

          feed_all.append(entry)

  return feed_all

      # ------------ FOR TESTING ------------------
      # print(item.title)
      # print(item.author)
      # print(item.link)
      # print(item.media_thumbnail[0]['url'])
      # print(clean_text)
