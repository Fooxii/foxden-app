import feedparser

source_list = ['https://www.pcgamer.com/rss.xml']

feed_all = []
for source in source_list:
  feed = feedparser.parse(source)
  for item in feed.entries:
    feed_all.append(f'{item.title} \n')

for item in feed_all:
  print(item)
