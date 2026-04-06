import { useState } from "react"
import AmbientBlobBackground from "@/components/AmbientBlobBackground"
import ChatHeader from "./components/ChatHeader"
import ChatMain from "./components/ChatMain"
import ChatInputBar from "./components/ChatInputBar"
import { authenticatedFetch } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"

function ChatPage() {
  const { user, logout } = useAuth()
  const [inputText, setInputText] = useState("")
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async (text) => {
    const userMsg = {
      type: "human",
      content: text,
      name: String(user.id),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInputText("")
    setIsLoading(true)

    try {
      const allMsgs = [...messages.filter((m) => !m.failed), userMsg]
      const payload = { messages: allMsgs }

      const res = await authenticatedFetch("/api/agents/user", {
        method: "POST",
        body: JSON.stringify(payload),
      })

      if (res.status === 401) {
        logout()
        return
      }

      if (!res.ok) {
        throw new Error(`API error ${res.status}`)
      }

      const data = await res.json()
      setMessages(data.messages ?? data)
    } catch {
      setMessages((prev) =>
        prev.map((m, i) =>
          i === prev.length - 1 ? { ...m, failed: true } : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative flex h-dvh w-full flex-col overflow-hidden bg-background text-foreground">
      <AmbientBlobBackground />

      <div className="relative flex h-full flex-1 flex-col">
        <ChatHeader />
        <ChatMain messages={messages} username={user.username} />

        <footer className="flex min-h-0 w-full flex-col items-center px-3 pb-3 pt-2">
          <ChatInputBar
            variant="no split"
            value={inputText}
            onChange={setInputText}
            onSend={handleSend}
            isLoading={isLoading}
          />
        </footer>
      </div>
    </div>
  )
}

export default ChatPage
