import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../supabase'
import { validatePassword } from '../utils/validation'
import './Auth.css'

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    const validationError = validatePassword(password)
    if (validationError) return setError(validationError)

    if (password !== confirmPassword) return setError('Passwords do not match.')

    setLoading(true)
    const { error } = await supabase.auth.updateUser({ password })
    setLoading(false)

    if (error) return setError(error.message)
    navigate('/feed')
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Set a new password.</h1>
        {error && <p className="error-msg">{error}</p>}
        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="input-group">
            <label>New password</label>
            <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <div className="input-group">
            <label>Confirm new password</label>
            <input type="password" placeholder="••••••••" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          </div>
          <p className="field-hint">8–20 characters, with at least one letter and one number.</p>
          <button type="submit" className="btn-primary" disabled={loading}>{loading ? 'Updating...' : 'Update password'}</button>
        </form>
      </div>
    </div>
  )
}
