# THE EMBEDDING GENERATOR FILE WILL GENERATE VECTOR EMBEDDINGS FOR ARTICLES AND TAGS USING SENTENCE TRANSFORMERS
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Basic function to generate embedding with provided text
def generate_embedding(text):
  if not text:
    return None

  embedding = model.encode(text)
  return embedding.tolist()


# Generates embedding using article title and content as the text
def generate_article_embedding(article):
  text = f"{article['title']} {article['content']}"
  return generate_embedding(text)


# Generates embedding using tag name and keywords as text
def generate_tag_embedding(tag):
  keywords = ' '.join(tag['keywords']) if tag.get('keywords') else ''
  text = f"{tag['name']} {keywords}"
  return generate_embedding(text)
