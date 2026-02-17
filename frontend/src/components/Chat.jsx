import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authenticatedFetch } from '../utils/api'

const API_URL = '/api/agents/user'
const STORAGE_KEY_PREFIX = 'bot_session_conversation_'

// Normalize message to internal format (type, content, failed?, name?)
// Handles legacy format with role -> type
const normalizeMessage = (m) => {
  if (Array.isArray(m)) {
    const [role, content] = m
    return {
      type: role === 'user' ? 'human' : 'ai',
      content: content || '',
      failed: false,
    }
  }
  const type = m.type ?? (m.role === 'user' ? 'human' : 'ai')
  return {
    type,
    content: m.content || '',
    failed: m.failed ?? false,
    name: m.name,
  }
}

const getStorageKey = (userId) => {
  if (!userId) return null
  return `${STORAGE_KEY_PREFIX}${userId}`
}

const saveConversation = (userId, messages, suggestions) => {
  try {
    const key = getStorageKey(userId)
    if (!key) return

    if (messages.length > 0) {
      const data = { messages, suggestions, userId }
      localStorage.setItem(key, JSON.stringify(data))
    }
    // Don't remove when empty - only clearConversation/clearAllConversations do that.
    // Removing here caused a race: save effect runs with [] before load completes, wiping persisted data.
  } catch (err) {
    console.error('Failed to save conversation to localStorage:', err)
  }
}

const loadConversation = (userId) => {
  try {
    const key = getStorageKey(userId)
    if (!key) return { messages: [], suggestions: [] }

    const stored = localStorage.getItem(key)
    if (stored) {
      const data = JSON.parse(stored)
      if (data.userId === userId) {
        const messages = (data.messages || []).map(normalizeMessage)
        return {
          messages,
          suggestions: data.suggestions || [],
        }
      } else {
        localStorage.removeItem(key)
      }
    }
  } catch (err) {
    console.error('Failed to load conversation from localStorage:', err)
  }
  return { messages: [], suggestions: [] }
}

const clearConversation = (userId) => {
  try {
    const key = getStorageKey(userId)
    if (key) {
      localStorage.removeItem(key)
    }
  } catch (err) {
    console.error('Failed to clear conversation from localStorage:', err)
  }
}

const clearAllConversations = () => {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(STORAGE_KEY_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  } catch (err) {
    console.error('Failed to clear all conversations from localStorage:', err)
  }
}

const Chat = () => {
  const [messages, setMessages] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef(null)
  const inputContainerRef = useRef(null)
  const greetingSentRef = useRef(false)
  const { user, logout } = useAuth()
  const hadUserRef = useRef(false)
  const navigate = useNavigate()

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  useEffect(() => {
    if (user?.id) {
      // Keep only 1 chat history: clear any other users' conversations when switching users
      const currentKey = getStorageKey(user.id)
      const keys = Object.keys(localStorage)
      keys.forEach((key) => {
        if (key.startsWith(STORAGE_KEY_PREFIX) && key !== currentKey) {
          localStorage.removeItem(key)
        }
      })

      const persisted = loadConversation(user.id)
      if (persisted.messages.length > 0) {
        setMessages(persisted.messages)
        setSuggestions(persisted.suggestions)
        greetingSentRef.current = true
      } else {
        setMessages([])
        setSuggestions([])
        greetingSentRef.current = false
      }
    } else {
      setMessages([])
      setSuggestions([])
      greetingSentRef.current = false
    }
  }, [user?.id])

  useEffect(() => {
    if (user?.id) {
      saveConversation(user.id, messages, suggestions)
    }
  }, [user?.id, messages, suggestions])

  useEffect(() => {
    // Only clear when user explicitly logs out (had user, now null). Never clear on initial load/refresh.
    if (user) {
      hadUserRef.current = true
    } else if (hadUserRef.current) {
      clearAllConversations()
      setMessages([])
      setSuggestions([])
      hadUserRef.current = false
    }
  }, [user])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const sendGreeting = async () => {
      if (!user?.id || messages.length > 0 || isLoading || greetingSentRef.current) {
        return
      }

      greetingSentRef.current = true
      setIsLoading(true)
      setError('')

      try {
        const res = await authenticatedFetch(API_URL, {
          method: 'POST',
          body: JSON.stringify({ messages: [] }),
        })

        if (!res.ok) {
          if (res.status === 401) {
            logout()
            navigate('/login')
            return
          }
          throw new Error(`Request failed with status ${res.status}`)
        }

        const data = await res.json()
        let backendMessages = []
        let backendSuggestions = []

        if (data.messages) {
          backendMessages = data.messages
          backendSuggestions = data.suggestions || []
        } else if (Array.isArray(data)) {
          backendMessages = data
          backendSuggestions = []
        }

        setMessages(backendMessages.map(m => ({ ...normalizeMessage(m), failed: false })))
        setSuggestions(backendSuggestions)
      } catch (err) {
        console.error('Error sending greeting', err)
        setError(err.message || 'Failed to load greeting')
        greetingSentRef.current = false
      } finally {
        setIsLoading(false)
      }
    }

    sendGreeting()
  }, [user?.id, messages.length, isLoading, logout, navigate])

  const sendMessage = async () => {
    const text = inputValue.trim()
    if (!text || isLoading) return

    const newMsg = { type: 'human', content: text, failed: false }
    if (user?.id) newMsg.name = user.id
    const nextMessages = [...messages, newMsg]
    setMessages(nextMessages)
    setInputValue('')
    setIsLoading(true)
    setError('')
    setSuggestions([])

    try {
      const messagesForBackend = nextMessages
        .filter((m) => !m.failed)
        .map(({ type, content }) => {
          const msg = { type, content }
          if (type === 'human' && user?.id) msg.name = user.id
          return msg
        })

      const res = await authenticatedFetch(API_URL, {
        method: 'POST',
        body: JSON.stringify({ messages: messagesForBackend }),
      })

      if (!res.ok) {
        if (res.status === 401) {
          logout()
          navigate('/login')
          return
        }
        throw new Error(`Request failed with status ${res.status}`)
      }

      const data = await res.json()
      let backendMessages = []
      let backendSuggestions = []

      if (data.messages) {
        backendMessages = data.messages
        backendSuggestions = data.suggestions || []
      } else if (Array.isArray(data)) {
        backendMessages = data
        backendSuggestions = []
      }

      setMessages(
        backendMessages.map((m) => ({
          ...normalizeMessage(m),
          failed: false,
        }))
      )
      setSuggestions(backendSuggestions)
    } catch (err) {
      console.error('Error sending message', err)
      setError(err.message || 'Failed to send message')
      setMessages((prevMessages) => {
        const updated = [...prevMessages]
        const lastIndex = updated.length - 1
        if (lastIndex >= 0 && updated[lastIndex].type === 'human') {
          updated[lastIndex] = { ...updated[lastIndex], failed: true }
        }
        return updated
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion)
  }

  const handleNewChat = () => {
    setMessages([])
    setSuggestions([])
    setInputValue('')
    setError('')
    greetingSentRef.current = false
    if (user?.id) {
      clearConversation(user.id)
    }
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <div className="app theme-neon">
      <div className="chat-container">
        <header className="chat-header">
          <div>
            <h1>🎲 Chat Agent</h1>
          </div>
          <div className="header-user-section">
            {user && (
              <div className="user-info">
                <span className="username-value">{user.username || user.email}</span>
                <button className="icon-button new-chat-button" onClick={handleNewChat} title="New Chat">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    <line x1="9" y1="10" x2="15" y2="10" />
                    <line x1="12" y1="7" x2="12" y2="13" />
                  </svg>
                </button>
                <button className="icon-button logout-button" onClick={logout} title="Logout">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </header>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Start a conversation with the agent!</p>
              <p className="hint">Try asking about users, games, or events.</p>
            </div>
          )}

          {messages.map((m, index) => {
            const isLastAssistantMessage =
              !isLoading &&
              m.type === 'ai' &&
              index === messages.length - 1 &&
              suggestions.length > 0

            return (
              <div
                key={index}
                className={`message ${m.type === 'human' ? 'message-user' : 'message-assistant'}`}
              >
                {m.type === 'human' && m.failed && (
                  <svg
                    className="message-failed-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    title="Message failed to send"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                )}
                <div className="message-content">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
                {isLastAssistantMessage && (
                  <div className="suggestions-container">
                    {suggestions.map((suggestion, sugIndex) => (
                      <button
                        key={sugIndex}
                        className="suggestion-button"
                        onClick={() => handleSuggestionClick(suggestion)}
                        disabled={isLoading}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          })}

          {isLoading && (
            <div className="message message-assistant">
              <div className="message-content loading">
                <span className="typing-indicator">
                  <span />
                  <span />
                  <span />
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && <div className="error-message">Error: {error}</div>}

        <div className="input-container" ref={inputContainerRef}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
            className="message-input"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default Chat
