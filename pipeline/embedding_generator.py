# THE EMBEDDING GENERATOR FILE WILL GENERATE VECTOR EMBEDDINGS FOR ARTICLES AND TAGS USING SENTENCE TRANSFORMERS

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def generate_embedding(text):
  if not text:
    return None

  embedding = model.encode(text)
  return embedding.tolist()


def generate_article_embedding(article):
  text = f"{article['title']} {article['content']}"
  return generate_embedding(text)


def generate_tag_embedding(tag):
  keywords = ' '.join(tag['keywords']) if tag.get('keywords') else ''
  text = f"{tag['name']} {keywords}"
  return generate_embedding(text)
