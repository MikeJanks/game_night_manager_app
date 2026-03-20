import { ScrollArea } from "@/components/ui/scroll-area"
import ChatEmptyState from "./ChatEmptyState"
import ChatMessage from "./ChatMessage"
import { AvatarFallback } from "@/components/ui/avatar"

const ChatMain = ({ messages = [] }) => {
  const hasMessages = messages.length > 0

  const botAvatar = (
    <AvatarFallback className="bg-transparent text-primary">
      <span className="font-material-symbols text-primary text-xl">smart_toy</span>
    </AvatarFallback>
  )
  const personAvatar = (
    <AvatarFallback className="bg-transparent text-primary">
      <span className="font-material-symbols text-primary text-xl">person</span>
    </AvatarFallback>
  )

  return (
    <ScrollArea className="flex-1 min-h-0">
      <main className="flex flex-col items-center w-full px-6 py-8">
        <div className="flex flex-col w-full max-w-3xl gap-8">
          {!hasMessages ? (
            <ChatEmptyState />
          ) : (
            messages.map((m, idx) => (
              <ChatMessage
                key={idx}
                side={m.role === "user" ? "right" : "left"}
                senderLabel={m.senderLabel}
                content={m.content}
                avatar={m.role === "bot"
                  ? botAvatar
                  : personAvatar
                }
              />
            ))
          )}
        </div>
      </main>
    </ScrollArea>
  )
}

export default ChatMain

