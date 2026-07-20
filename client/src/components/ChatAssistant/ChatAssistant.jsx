import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { sendChatMessage } from '../../services/chatService'
import './ChatAssistant.css'

export default function ChatAssistant() {
  const { user } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [remaining, setRemaining] = useState(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, loading])

  if (!user) return null

  const handleSend = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return

    setError(null)
    setInput('')
    const nextMessages = [...messages, { role: 'user', content: text }]
    setMessages(nextMessages)
    setLoading(true)

    try {
      const historyForApi = nextMessages.slice(0, -1).map(({ role, content }) => ({ role, content }))
      const result = await sendChatMessage(text, historyForApi)
      setMessages((prev) => [...prev, { role: 'assistant', content: result.reply }])
      setRemaining(result.remaining)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-assistant">
      {isOpen && (
        <div className="chat-panel">
          <div className="chat-header">
            <span>FoxDen Assistant</span>
            <button className="chat-close" onClick={() => setIsOpen(false)}>×</button>
          </div>

          <div className="chat-messages" ref={scrollRef}>
            {messages.length === 0 && (
              <p className="chat-empty">Ask me how to use FoxDen — following tags, pinning, custom tags, and more.</p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>{m.content}</div>
            ))}
            {loading && <div className="chat-bubble assistant typing">...</div>}
          </div>

          {error && <p className="chat-error">{error}</p>}
          {remaining !== null && !error && (
            <p className="chat-remaining">{remaining} message{remaining !== 1 ? 's' : ''} left today</p>
          )}

          <form className="chat-input-row" onSubmit={handleSend}>
            <input
              type="text"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>Send</button>
          </form>
        </div>
      )}

      <button className="chat-toggle" onClick={() => setIsOpen((o) => !o)}>
        {isOpen ? '×' : '💬'}
      </button>
    </div>
  )
}
