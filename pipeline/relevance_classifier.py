# THE RELEVANCE CLASSIFIER WILL USE THE ZERO-SHOT CLASSIFICATION MODEL TO CLASSIFY IF A TAG IS RELATED TO AN ARTICLE

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


def build_classification_label(name, is_official, detail=""):
  # official tag names (Gaming, PC Hardware, AI...) already read as natural
  # zero-shot labels on their own. custom tags are user-invented names
  # (e.g. "Valve Devices") that carry little meaning by themselves — folding
  # in a short piece of the user's own description gives the model
  # something concrete to actually judge the article against
  if is_official or not detail:
    return name
  return f"{name} ({detail[:120]})"


def classify_text_against_labels(text, label_map):
  # label_map: { display_name: classification_label_text }
  if not label_map:
    return {}

  classifier = get_classifier()
  classification_labels = list(label_map.values())

  result = classifier(text[:1000], candidate_labels=classification_labels, multi_label=True)

  label_to_name = {v: k for k, v in label_map.items()}

  matches = {}
  for label_text, score in zip(result["labels"], result["scores"]):
    if score >= FINAL_MATCH_THRESHOLD:
      display_name = label_to_name.get(label_text, label_text)
      matches[display_name] = round(score, 4)
  return matches


def classify_texts_against_label(texts, label):
  # inverse of the function above: one label, many texts, batched into a
  # single classifier call instead of looping — this is what keeps
  # backfilling a new tag against many existing articles fast
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
