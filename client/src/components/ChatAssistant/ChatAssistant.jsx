import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { sendChatMessage } from '../../services/chatService'
import './ChatAssistant.css'

const WELCOME_MESSAGE = {
  role: 'assistant',
  content: "Hi! I'm the FoxDen assistant. Ask me how to use the app — following tags, pinning, custom tags, sorting your feed, or anything else you need help with.",
  isWelcome: true,
}

export default function ChatAssistant() {
  const { user } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [remaining, setRemaining] = useState(null)
  const [limitReached, setLimitReached] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, loading])

  if (!user) return null

  const handleSend = async (e) => {
    e.preventDefault()
    const text = input.trim()

    if (!text || loading || limitReached) return

    setLoading(true)
    setInput('')
    setError(null)

    const nextMessages = [...messages, { role: 'user', content: text }]
    setMessages(nextMessages)

    try {
      const historyForApi = nextMessages
        .filter((m) => !m.isWelcome && !m.isLimitMessage)
        .slice(0, -1)
        .map(({ role, content }) => ({ role, content }))

      const result = await sendChatMessage(text, historyForApi)

      if (result.limitReached) {
        setLimitReached(true)
        setRemaining(0)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `You've reached your daily limit of ${result.limit} messages. Your limit resets at midnight UTC. Come back tomorrow!`,
            isLimitMessage: true,
          }
        ])
      } else {
        setMessages((prev) => [...prev, { role: 'assistant', content: result.reply }])
        setRemaining(result.remaining)
        if (result.remaining === 0) setLimitReached(true)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!loading && !limitReached && input.trim()) {
        handleSend(e)
      }
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
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role} ${m.isWelcome ? 'welcome' : ''} ${m.isLimitMessage ? 'limit' : ''}`}>
                {m.content}
              </div>
            ))}
            {loading && (
              <div className="chat-bubble assistant typing">
                Thinking... (this may take a few seconds)
              </div>
            )}
          </div>

          {error && <p className="chat-error">{error}</p>}

          {remaining !== null && !error && (
            <p className={`chat-remaining ${limitReached ? 'zero' : ''}`}>
              {limitReached
                ? '0 messages left today'
                : `${remaining} message${remaining !== 1 ? 's' : ''} left today`}
            </p>
          )}

          <form className="chat-input-row" onSubmit={handleSend}>
            <input
              type="text"
              placeholder={limitReached ? 'Daily limit reached' : 'Ask a question...'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading || limitReached}
            />
            <button type="submit" disabled={loading || !input.trim() || limitReached}>
              {loading ? '...' : 'Send'}
            </button>
          </form>
        </div>
      )}

      <button className="chat-toggle" onClick={() => setIsOpen((o) => !o)}>
        {isOpen ? '×' : '💬'}
      </button>
    </div>
  )
}
