export function validatePassword(password) {
  if (!password || password.trim() === '') {
    return 'Password is required.'
  }
  if (password.length < 8) {
    return 'Password must be at least 8 characters.'
  }
  if (password.length > 20) {
    return 'Password must be 20 characters or fewer.'
  }
  if (!/[a-zA-Z]/.test(password)) {
    return 'Password must contain at least one letter.'
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one number.'
  }
  return null
}
