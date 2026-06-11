import { supabase } from '../supabase'

async function handleSignUp(email, password) {
  const { data, error } = await supabase.auth.signUp({ email, password })
  if (error) console.log(error)
}

async function handleLogin(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) console.log(error)
}

export default function SignupPage() {
  return (
    <div className='page-wrapper'>
        Signup Page
    </div>
  )
}
