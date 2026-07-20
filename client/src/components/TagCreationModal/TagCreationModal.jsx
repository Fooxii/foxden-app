import { useState } from 'react'
import { createCustomTag } from '../../services/tagService'
import './TagCreationModal.css'

export default function TagCreationModal({ userId, onClose, onCreated }) {
  const [name, setName] = useState('')
  const [interestDescription, setInterestDescription] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCreate = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const newTag = await createCustomTag(userId, name, interestDescription)
      onCreated(newTag)
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Create a custom tag</h2>
        <p className="modal-subtitle">Give your tag a name, then tell us what you want it to cover. It'll start matching articles within about 20 seconds.</p>
        {error && <p className="error-msg">{error}</p>}
        <form onSubmit={handleCreate}>
          <div className="input-group">
            <label>Tag name</label>
            <input type="text" placeholder="e.g. PC Hardware" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="input-group">
            <label>I want to follow news related to:</label>
            <textarea placeholder="e.g. graphics cards, GPU benchmarks, and gaming performance" value={interestDescription} onChange={(e) => setInterestDescription(e.target.value)} rows={3} required />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={loading}>{loading ? 'Creating...' : 'Create tag'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}
