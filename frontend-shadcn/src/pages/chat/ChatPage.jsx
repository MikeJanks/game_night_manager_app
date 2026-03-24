import { useState } from "react"
import AmbientBlobBackground from "@/components/AmbientBlobBackground"
import ChatHeader from "./components/ChatHeader"
import ChatMain from "./components/ChatMain"
import ChatInputBar from "./components/ChatInputBar"

function ChatPage() {
  const [inputText, setInputText] = useState("")

  const [messages, setMessages] = useState([
    // {
    //   role: "bot",
    //   senderLabel: "Game Night Manager",
    //   content: "Ready to schedule our next DnD session? I see everyone is active in the group."
    // },
    // {
    //   role: "user",
    //   senderLabel: "Mike",
    //   content: "How does Friday at 7 PM work for everyone?"
    // },
    // {
    //   role: "bot",
    //   senderLabel: "Game Night Manager",
    //   content: "I've checked the group's availability. Friday at 7 PM looks perfect for all 5 players. Should I add it to the shared calendar and send the invites?"
    // },
    // {
    //   role: "user",
    //   senderLabel: "Mike",
    //   content: "Yes, please! Let's get that campaign started. I've been waiting all week."
    // }
  ])

  return (
    <div className="relative flex h-dvh w-full flex-col overflow-hidden bg-background text-foreground">
      <AmbientBlobBackground />

      <div className="relative flex h-full flex-1 flex-col">
        <ChatHeader />
        <ChatMain
          messages={messages}
        />

        <footer className="flex min-h-0 w-full flex-col items-center px-6 pb-8 pt-2">
          <ChatInputBar
            variant="no split"
            value={inputText}
            onChange={setInputText}
            onSend={(text) => {
              setMessages((m) => [
                ...m,
                { role: "user", senderLabel: "Mike", content: text },
              ])
              setInputText("")
            }}
          />
        </footer>
      </div>
    </div>
  )
}

export default ChatPage
