import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase } from '../../supabase'
import { validatePassword } from '../../utils/validation'
import '../Auth.css'

export default function SignUpPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [officialTags, setOfficialTags] = useState([])
  const [selectedTagIds, setSelectedTagIds] = useState(new Set())
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    supabase.from('tags').select('id, name').eq('is_official', true).order('name')
      .then(({ data }) => setOfficialTags(data || []))
  }, [])

  const toggleTag = (tagId) => {
    setSelectedTagIds((prev) => {
      const next = new Set(prev)
      next.has(tagId) ? next.delete(tagId) : next.add(tagId)
      return next
    })
  }

  const handleSignUp = async (e) => {
    e.preventDefault()
    setError(null)

    const passwordError = validatePassword(password)
    if (passwordError) { setError(passwordError); return }

    if (selectedTagIds.size < 3) {
      setError('Pick at least 3 tags to personalize your feed.')
      return
    }

    setLoading(true)

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/feed`,
        data: {
          name: name.trim(),
          tag_ids: Array.from(selectedTagIds)
        }
      }
    })

    setLoading(false)

    if (error) { setError(error.message); return }

    if (data.session) {
      navigate('/feed')
    } else {
      setMessage('Account created! Check your email to confirm, then you can log in.')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create your account.</h1>
        {error && <p className="error-msg">{error}</p>}
        {message && <p className="success-msg">{message}</p>}
        <form className="form-stack" onSubmit={handleSignUp}>
          <div className="input-group">
            <label>Full name</label>
            <input type="text" placeholder="Name LastName" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="input-group">
            <label>Email</label>
            <input type="email" placeholder="email@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <p className="field-hint">8–20 characters, with at least one letter and one number.</p>
          </div>

          <div className="onboarding-tags">
            <h3>What are you into?</h3>
            <p>Pick at least 3 tags to personalize your feed. You can always change these later.</p>
            <div className="tag-suggest-grid">
              {officialTags.map((tag) => (
                <button type="button" key={tag.id}
                  className={`suggest-pill ${selectedTagIds.has(tag.id) ? 'active' : ''}`}
                  onClick={() => toggleTag(tag.id)}>
                  {tag.name}
                </button>
              ))}
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>
        <p className="auth-footer">Already have an account? <Link to="/login">Log in</Link></p>
      </div>
    </div>
  )
}
