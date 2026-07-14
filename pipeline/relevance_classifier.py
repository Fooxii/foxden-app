# STAGE 1: CHEAP EMBEDDING-BASED SHORTLIST (HIGH RECALL)
# STAGE 2: ACCURATE NLI ZERO-SHOT CLASSIFICATION OVER THE SHORTLIST (HIGH PRECISION)
# fully local — no external API, no rate limits, no network dependency

from transformers import pipeline
import numpy as np
import json

SHORTLIST_COSINE_THRESHOLD = 0.20
SHORTLIST_MAX_CANDIDATES = 15
FINAL_MATCH_THRESHOLD = 0.55

_classifier = None


def get_classifier():
  global _classifier
  if _classifier is None:
    _classifier = pipeline(
      "zero-shot-classification",
      model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
    )
  return _classifier


def parse_embedding(value):
  return json.loads(value) if isinstance(value, str) else value


def cosine_similarity(vec_a, vec_b):
  a = np.array(vec_a)
  b = np.array(vec_b)
  return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def shortlist_candidates(target_embedding, pool, embedding_field="embedding"):
  scored = []
  for item in pool:
    emb = item.get(embedding_field)
    if not emb:
      continue
    score = cosine_similarity(target_embedding, parse_embedding(emb))
    if score >= SHORTLIST_COSINE_THRESHOLD:
      scored.append((item, score))
  scored.sort(key=lambda x: x[1], reverse=True)
  return [item for item, _ in scored[:SHORTLIST_MAX_CANDIDATES]]


def classify_text_against_labels(text, label_names):
  if not label_names:
    return {}

  classifier = get_classifier()
  result = classifier(text[:1000], candidate_labels=label_names, multi_label=True)

  return {
    label: round(score, 4)
    for label, score in zip(result["labels"], result["scores"])
    if score >= FINAL_MATCH_THRESHOLD
  }
