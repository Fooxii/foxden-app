const express = require('express')
const router = express.Router()
const supabase = require('../supabase')

// called after supabase auth signup to store profile data
router.post('/register', async (req, res) => {
  const { id, name, email } = req.body

  const { data, error } = await supabase
    .from('users')
    .insert([{ id, name, email }])

  if (error) return res.status(400).json({ error: error.message })
  res.status(201).json({ data })
})

module.exports = router
