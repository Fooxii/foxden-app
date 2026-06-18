import { useState } from 'react'
import { supabase } from '../supabase'
import { Link } from 'react-router-dom'

export default function SignUpPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)

  const handleSignUp = async (e) => {
    e.preventDefault()
    setError(null)

    // step 1 — create auth account in supabase
    const { data, error: authError } = await supabase.auth.signUp({
      email,
      password
    })

    if (authError) return setError(authError.message)

    // step 2 — store profile in your users table
    const res = await fetch('http://localhost:3000/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: data.user.id,
        name,
        email
      })
    })

    const result = await res.json()
    if (result.error) return setError(result.error)

    setMessage('Account created! Check your email to confirm.')
  }

  return (
    <div className='signup-page'>
      <h1>Create your account.</h1>
      {error && <p className='error-msg'>{error}</p>}
      {message && <p className='success-msg'>{message}</p>}
      <form onSubmit={handleSignUp}>
        <div className='input-group'>
          <label>Full name</label>
          <input
            type='text'
            placeholder='Name LastName'
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className='input-group'>
          <label>Email</label>
          <input
            type='email'
            placeholder='email@email.com'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className='input-group'>
          <label>Password</label>
          <input
            type='password'
            placeholder='••••••••'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type='submit'>Create account</button>
      </form>
      <p>Already have an account? <Link to='/login'>Log in</Link></p>
    </div>
  )
}
