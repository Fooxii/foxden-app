import { pipeline, env } from '@xenova/transformers'

console.log('[embeddingService] loaded v2 — allowLocalModels:', false)

env.allowLocalModels = false
env.useBrowserCache = true

let extractorPromise = null

export function preloadEmbeddingModel() {
  if (!extractorPromise) {
    console.log('[embeddingService] starting model download...')
    extractorPromise = pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2')
      .then((p) => { console.log('[embeddingService] model ready'); return p })
      .catch((err) => { console.error('[embeddingService] model load failed:', err); throw err })
  }
  return extractorPromise
}

export async function generateEmbedding(text) {
  const extractor = await preloadEmbeddingModel()
  const output = await extractor(text, { pooling: 'mean', normalize: true })
  return Array.from(output.data)
}

export function parseEmbedding(value) {
  return typeof value === 'string' ? JSON.parse(value) : value
}

export function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i]
    normA += a[i] * a[i]
    normB += b[i] * b[i]
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB))
}
