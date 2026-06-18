import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../supabase'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError(null)

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) return setError(error.message)

    navigate('/feed')
  }

  return (
    <div className='login-page'>
      <h1>Log in Page</h1>
      {error && <p className='error-msg'>{error}</p>}
      <form onSubmit={handleLogin}>
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
        <button type='submit'>Log in</button>
      </form>
      <p>Don't have an account? <a href='/signup'>Sign up</a></p>
    </div>
  )
}
