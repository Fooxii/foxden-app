import { useState } from 'react'
import { createCustomTag } from '../../services/tagService'
import './TagCreationModal.css'

const MAX_NAME_LENGTH = 50
const MAX_INTEREST_LENGTH = 500

export default function TagCreationModal({ userId, onClose, onCreated }) {
  const [name, setName] = useState('')
  const [interestDescription, setInterestDescription] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const nameOverLimit = name.length > MAX_NAME_LENGTH
  const interestOverLimit = interestDescription.length > MAX_INTEREST_LENGTH
  const isOverLimit = nameOverLimit || interestOverLimit

  const handleCreate = async (e) => {
    e.preventDefault()
    if (isOverLimit) return

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

  const getCounterClass = (current, max) => {
    if (current > max) return 'counter error'
    if (current > max * 0.9) return 'counter warning'
    return 'counter'
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Create a custom tag</h2>
        <p className="modal-subtitle">
          Give your tag a name and tell us what you want it to cover. It'll start matching articles within minutes.
        </p>
        {error && <p className="error-msg">{error}</p>}

        <form onSubmit={handleCreate}>
          <div className="input-group">
            <label htmlFor="tag-name">Tag name</label>
            <input
              id="tag-name"
              type="text"
              placeholder="Tag Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={MAX_NAME_LENGTH + 20}
              required
            />
            <span className={getCounterClass(name.length, MAX_NAME_LENGTH)}>
              {name.length}/{MAX_NAME_LENGTH}
            </span>
            {nameOverLimit && (
              <span className="validation-msg">
                Tag name must be {MAX_NAME_LENGTH} characters or less.
              </span>
            )}
          </div>

          <div className="input-group">
            <label htmlFor="tag-interest">I want to follow news related to:</label>
            <textarea
              id="tag-interest"
              placeholder={
                name
                  ? `Interests related to ${name}`
                  : 'Interests related to...'
              }
              value={interestDescription}
              onChange={(e) => setInterestDescription(e.target.value)}
              rows={3}
              maxLength={MAX_INTEREST_LENGTH + 200}
              required
            />
            <span className={getCounterClass(interestDescription.length, MAX_INTEREST_LENGTH)}>
              {interestDescription.length}/{MAX_INTEREST_LENGTH}
            </span>
            {interestOverLimit && (
              <span className="validation-msg">
                Description must be {MAX_INTEREST_LENGTH} characters or less.
              </span>
            )}
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || isOverLimit}
            >
              {loading ? 'Creating...' : 'Create tag'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
