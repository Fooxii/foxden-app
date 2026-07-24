# THE RELEVANCE CLASSIFIER WILL USE THE ZERO-SHOT CLASSIFICATION MODEL TO CLASSIFY IF A TAG IS RELATED TO AN ARTICLE

from transformers import pipeline
from sentence_transformers import CrossEncoder
import torch
import numpy as np
import json

SHORTLIST_COSINE_THRESHOLD = 0.20
SHORTLIST_MAX_CANDIDATES = 20
RERANK_TOP_N = 6
CUSTOM_TAG_RERANK_THRESHOLD = 0.30
FINAL_MATCH_THRESHOLD = 0.55

RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_classifier = None
_reranker = None


def get_classifier():
  global _classifier
  if _classifier is None:
    _classifier = pipeline(
      "zero-shot-classification",
      model="MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
      batch_size=8
    )
  return _classifier


def get_reranker():
  global _reranker
  if _reranker is None:
    _reranker = CrossEncoder(RERANK_MODEL_NAME)
  return _reranker


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


def rerank_candidates(query_text, candidates, get_candidate_text):
  if not candidates:
    return []
  reranker = get_reranker()
  pairs = [(query_text, get_candidate_text(c)) for c in candidates]
  scores = reranker.predict(pairs, activation_fn=torch.nn.Sigmoid())
  scored = list(zip(candidates, scores))
  scored.sort(key=lambda x: x[1], reverse=True)
  return [c for c, _ in scored[:RERANK_TOP_N]]


def rerank_score_all(query_text, candidates, get_candidate_text):
  if not candidates:
    return []
  reranker = get_reranker()
  pairs = [(query_text, get_candidate_text(c)) for c in candidates]
  scores = reranker.predict(pairs, activation_fn=torch.nn.Sigmoid())
  scored = list(zip(candidates, scores))
  scored.sort(key=lambda x: x[1], reverse=True)
  return scored


def build_classification_label(name, is_official, detail=""):
  if is_official or not detail:
    return name
  return f"{name}, such as {detail[:150]}"


def split_keywords(keyword_string):
  if not keyword_string:
    return []
  parts = [p.strip() for p in keyword_string.split(",")]
  return [p for p in parts if len(p) >= 3]


def text_contains_any_keyword(text, keyword_string):
  keywords = split_keywords(keyword_string)
  if not keywords:
    return False
  lowered_text = (text or "").lower()
  return any(kw.lower() in lowered_text for kw in keywords)


def keyword_match_articles(keyword_string, articles, get_text=None):
  if get_text is None:
    get_text = lambda a: f"{a['title']}. {a.get('content', '')}"
  return [a for a in articles if text_contains_any_keyword(get_text(a), keyword_string)]


def get_raw_classification_scores(text, label_map):
  if not label_map:
    return {}
  classifier = get_classifier()
  classification_labels = list(label_map.values())
  result = classifier(text[:1000], candidate_labels=classification_labels, multi_label=True)
  label_to_name = {v: k for k, v in label_map.items()}
  return {
    label_to_name.get(label_text, label_text): round(score, 4)
    for label_text, score in zip(result["labels"], result["scores"])
  }


def classify_text_against_labels(text, label_map):
  raw_scores = get_raw_classification_scores(text, label_map)
  return {name: score for name, score in raw_scores.items() if score >= FINAL_MATCH_THRESHOLD}


def classify_texts_against_label(texts, label):
  if not texts:
    return []
  classifier = get_classifier()
  results = classifier(texts, candidate_labels=[label], multi_label=True)
  if isinstance(results, dict):
    results = [results]
  scores = []
  for r in results:
    label_scores = dict(zip(r["labels"], r["scores"]))
    score = label_scores.get(label)
    scores.append(round(score, 4) if score is not None and score >= FINAL_MATCH_THRESHOLD else None)
  return scores
