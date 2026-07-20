import { useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../supabase'
import './Auth.css'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`
    })

    setLoading(false)
    if (error) return setError(error.message)
    setMessage('Check your email for a link to reset your password.')
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Reset your password.</h1>
        {error && <p className="error-msg">{error}</p>}
        {message && <p className="success-msg">{message}</p>}
        {!message && (
          <form className="form-stack" onSubmit={handleSubmit}>
            <div className="input-group">
              <label>Email</label>
              <input type="email" placeholder="email@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Sending...' : 'Send reset link'}
            </button>
          </form>
        )}
        <p className="auth-footer"><Link to="/login">Back to login</Link></p>
      </div>
    </div>
  )
}
