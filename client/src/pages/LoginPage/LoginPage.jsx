import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase } from '../../supabase'
import '../Auth.css'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [resending, setResending] = useState(false)
  const [resent, setResent] = useState(false)
  const navigate = useNavigate()

  const isUnconfirmedError = error && error.toLowerCase().includes('confirm')

  const handleLogin = async (e) => {
    e.preventDefault()
    setError(null)
    setResent(false)
    setLoading(true)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    setLoading(false)
    if (error) return setError(error.message)
    navigate('/feed')
  }

  const handleResend = async () => {
    setResending(true)
    const { error } = await supabase.auth.resend({ type: 'signup', email })
    setResending(false)
    if (error) setError(error.message)
    else setResent(true)
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Welcome back.</h1>
        {error && <p className="error-msg">{error}</p>}
        {isUnconfirmedError && !resent && (
          <button type="button" className="btn-ghost small" onClick={handleResend} disabled={resending}>
            {resending ? 'Sending...' : 'Resend confirmation email'}
          </button>
        )}
        {resent && <p className="success-msg">Confirmation email sent — check your inbox.</p>}
        <form className="form-stack" onSubmit={handleLogin}>
          <div className="input-group">
            <label>Email</label>
            <input type="email" placeholder="email@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <div className="label-row">
              <label>Password</label>
              <Link to="/forgot-password" className="inline-link">Forgot password?</Link>
            </div>
            <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button>
        </form>
        <p className="auth-footer">Don't have an account? <Link to="/signup">Sign up</Link></p>
      </div>
    </div>
  )
}
