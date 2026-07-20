import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../supabase'
import { validatePassword } from '../utils/validation'
import './Auth.css'

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(true)
  const [hasSession, setHasSession] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false

    const checkSession = async () => {
      // Try to get existing session
      const { data: { session } } = await supabase.auth.getSession()

      if (!cancelled) {
        if (session) {
          setHasSession(true)
          setVerifying(false)
        } else if (window.location.hash.includes('type=recovery') || window.location.hash.includes('access_token')) {
          // Tokens in URL but not processed yet — wait for auth state change
          const { data: { subscription } } = supabase.auth.onAuthStateChange((event, newSession) => {
            if (!cancelled && (event === 'PASSWORD_RECOVERY' || newSession)) {
              setHasSession(true)
              setVerifying(false)
              subscription.unsubscribe()
            }
          })

          // Safety timeout: if nothing happens in 5s, the link is probably invalid
          setTimeout(() => {
            if (!cancelled) {
              setVerifying(false)
              subscription.unsubscribe()
            }
          }, 5000)
        } else {
          // No tokens, no session — user navigated here directly
          setVerifying(false)
        }
      }
    }

    checkSession()
    return () => { cancelled = true }
  }, [])

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

  if (verifying) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h1>Verifying reset link...</h1>
          <p>Please wait while we verify your reset link.</p>
        </div>
      </div>
    )
  }

  if (!hasSession) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h1>Invalid or expired link</h1>
          <p className="error-msg">This password reset link is invalid or has expired.</p>
          <button className="btn-primary" onClick={() => navigate('/forgot-password')}>
            Request a new link
          </button>
        </div>
      </div>
    )
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
