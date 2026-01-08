import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authenticatedFetch } from '../utils/api'

const API_URL = '/agent/chat'
const STORAGE_KEY_PREFIX = 'agent_chat_conversation_'

// localStorage helper functions
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
    } else {
      // Remove empty conversations
      localStorage.removeItem(key)
    }
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
      // Verify the conversation belongs to this user
      if (data.userId === userId) {
        return {
          messages: data.messages || [],
          suggestions: data.suggestions || [],
        }
      } else {
        // Conversation belongs to different user, remove it
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

// Clear all conversations (useful when logging out)
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
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  // Load persisted conversation when user changes
  useEffect(() => {
    if (user?.id) {
      const persisted = loadConversation(user.id)
      if (persisted.messages.length > 0) {
        setMessages(persisted.messages)
        setSuggestions(persisted.suggestions)
      } else {
        // Clear state if no conversation for this user
        setMessages([])
        setSuggestions([])
      }
    } else {
      // No user logged in, clear everything
      setMessages([])
      setSuggestions([])
    }
  }, [user?.id])

  // Save conversation to localStorage when messages or suggestions change
  useEffect(() => {
    if (user?.id) {
      saveConversation(user.id, messages, suggestions)
    }
  }, [user?.id, messages, suggestions])

  // Clear conversations when user logs out
  useEffect(() => {
    if (!user) {
      clearAllConversations()
      setMessages([])
      setSuggestions([])
    }
  }, [user])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    const text = inputValue.trim()
    if (!text || isLoading) return

    const nextMessages = [...messages, { role: 'user', content: text, failed: false }]
    setMessages(nextMessages)
    setInputValue('')
    setIsLoading(true)
    setError('')
    setSuggestions([]) // Clear suggestions when sending a new message

    try {
      // Filter out failed messages and format as tuples [role, content] for LangGraph
      const messagesForBackend = nextMessages
        .filter((m) => !m.failed)
        .map(({ role, content }) => [role, content])
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
      
      // Handle new response format with messages and suggestions
      let backendMessages = []
      let backendSuggestions = []
      
      if (data.messages) {
        // New format: { messages: [...], suggestions: [...] }
        backendMessages = data.messages
        backendSuggestions = data.suggestions || []
      } else if (Array.isArray(data)) {
        // Legacy format: just array of messages
        backendMessages = data
        backendSuggestions = []
      }

      // Replace entire message history with backend response
      // Failed messages are naturally removed since they weren't sent to backend
      setMessages(
        backendMessages.map((m) => {
          const [role, content] = Array.isArray(m) ? m : [m.role || 'assistant', m.content || '']
          return {
            role,
            content,
            failed: false,
          }
        }),
      )
      
      // Update suggestions
      setSuggestions(backendSuggestions)
    } catch (err) {
      console.error('Error sending message', err)
      setError(err.message || 'Failed to send message')
      // Mark the last user message as failed
      setMessages((prevMessages) => {
        const updated = [...prevMessages]
        const lastIndex = updated.length - 1
        if (lastIndex >= 0 && updated[lastIndex].role === 'user') {
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
    // Optionally auto-send: sendMessage() after setting input
    // For now, just populate the input field
  }

  const handleNewChat = () => {
    setMessages([])
    setSuggestions([])
    setInputValue('')
    setError('')
    if (user?.id) {
      clearConversation(user.id)
    }
    // Scroll to top
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }
  
  useEffect(() => {
    const setAppHeight = () => {
      const vv = window.visualViewport;
      const height = vv ? vv.height : window.innerHeight;
      document.documentElement.style.setProperty('--app-height', `${height}px`);
    };
  
    setAppHeight();
  
    const vv = window.visualViewport;
    if (vv) {
      vv.addEventListener('resize', setAppHeight);
      vv.addEventListener('scroll', setAppHeight); // helps on iOS
    }
    window.addEventListener('resize', setAppHeight);
  
    return () => {
      if (vv) {
        vv.removeEventListener('resize', setAppHeight);
        vv.removeEventListener('scroll', setAppHeight);
      }
      window.removeEventListener('resize', setAppHeight);
    };
  }, []);

  return (
    <div className="app theme-neon">
      <div className="chat-container">
        <header className="chat-header">
          <div>
            <h1>Chat Agent</h1>
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
              m.role === 'assistant' && 
              index === messages.length - 1 &&
              suggestions.length > 0;
            
            return (
              <div
                key={index}
                className={`message ${m.role === 'user' ? 'message-user' : 'message-assistant'}`}
              >
                {m.role === 'user' && m.failed && (
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

