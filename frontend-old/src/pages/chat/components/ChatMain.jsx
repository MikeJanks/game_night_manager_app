import { useState } from 'react'
import { twMerge } from 'tailwind-merge'
import ChatEmptyState from './ChatEmptyState'
import ChatMessage from './ChatMessage'

const ChatMain = () => {
const [messages, setMessages] = useState([
  {
    role: "user",
    senderLabel: "Mike",
    content: "Is this message longer than 30 characters."
  },
  {
    role: "bot",
    senderLabel: "Game Night Manager",
    content: "I dont think that message is longer than 30 characters"
  },
  {
    role: "user",
    senderLabel: "Mike",
    content: "Is this message longer than 30 characters. Is this message longer than 30 characters. Is this message longer than 30 characters"
  },
  {
    role: "user",
    senderLabel: "Mike",
    content: "Is this message longer than 30 characters. Is this message longer than 30 characters. Is this message longer than 30 characters"
  },
  {
    role: "bot",
    senderLabel: "Game Night Manager",
    content: "I dont think that message is longer than 30 characters. I dont think that message is longer than 30 characters. I dont think that message is longer than 30 characters"
  }
])

  return (
    <main className="flex-1 flex flex-col gap-8 overflow-y-auto py-8">
      {
        !messages?.length > 0
          ? <ChatEmptyState />
          : messages.map(({role, senderLabel, content}, i) =>
            <div key={i} className={twMerge(`w-full`, `${role==="user" ? "self-end" : "self-start"}`)}>
              <ChatMessage role={role} senderLabel={senderLabel} content={content}/>
            </div>
          )
      }
    </main>
  )
}

export default ChatMain

