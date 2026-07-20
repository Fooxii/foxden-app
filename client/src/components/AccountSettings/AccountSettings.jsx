import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import { deleteCustomTag } from '../../services/tagService'
import { deleteAccount } from '../../services/userService'
import './AccountSettings.css'

export default function AccountSettings({ customTags, onTagDeleted }) {
  const { theme, toggleTheme } = useTheme()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState(null)

  const handleDeleteTag = async (tagId) => {
    try {
      await deleteCustomTag(tagId, user.id)
      onTagDeleted()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteAccount = async () => {
    setDeleting(true)
    try {
      await deleteAccount(user.id)
      await signOut()
      navigate('/signup')
    } catch (err) {
      setError(err.message)
      setDeleting(false)
    }
  }

  return (
    <div className="settings-section">
      <h3>Settings</h3>
      {error && <p className="error-msg">{error}</p>}

      <div className="settings-row">
        <div>
          <p className="settings-label">Appearance</p>
          <p className="settings-sub">Choose how FoxDen looks on your device.</p>
        </div>
        <div className="theme-switch">
          <button className={theme === 'light' ? 'active' : ''} onClick={() => theme === 'dark' && toggleTheme()}>Light</button>
          <button className={theme === 'dark' ? 'active' : ''} onClick={() => theme === 'light' && toggleTheme()}>Dark</button>
        </div>
      </div>

      <div className="settings-row">
        <div>
          <p className="settings-label">Notifications</p>
          <p className="settings-sub">Per-tag alerts are coming in a future update.</p>
        </div>
        <span className="coming-soon">Coming soon</span>
      </div>

      {customTags.length > 0 && (
        <div className="settings-block">
          <p className="settings-label">Your custom tags</p>
          <div className="custom-tag-manage-list">
            {customTags.map((tag) => (
              <div className="custom-tag-manage-row" key={tag.id}>
                <span>{tag.name}</span>
                <button className="btn-ghost danger small" onClick={() => handleDeleteTag(tag.id)}>Delete</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="settings-block danger-zone">
        <p className="settings-label">Danger zone</p>
        <p className="settings-sub">Permanently delete your account, saved articles, and custom tags. This cannot be undone.</p>
        {!confirming ? (
          <button className="btn-ghost danger" onClick={() => setConfirming(true)}>Delete account</button>
        ) : (
          <div className="confirm-delete">
            <p>Are you sure? This is permanent.</p>
            <div className="confirm-actions">
              <button className="btn-ghost" onClick={() => setConfirming(false)}>Cancel</button>
              <button className="btn-danger" onClick={handleDeleteAccount} disabled={deleting}>
                {deleting ? 'Deleting...' : 'Yes, delete everything'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}