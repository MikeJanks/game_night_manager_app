import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ChatMarkdownContent } from "@/components/ChatMarkdownContent"
import { getInitials } from "@/lib/getInitials"
import { cn } from "@/lib/utils"

const ChatMessage = ({ side = "left", senderLabel, content, avatar, markdown = false }) => {
  const isRight = side === "right"
  const avatarFallback = getInitials(senderLabel)

  return (
    <div className={cn("flex min-w-0 items-start gap-4", isRight && "flex-row-reverse")}>
      <Avatar size="lg" className="shrink-0 border border-border bg-card">
        {avatar
          ? avatar // <AvatarImage src={avatarSrc} alt={senderLabel} />
          : <AvatarFallback className="bg-transparent text-primary">{avatarFallback}</AvatarFallback>
        }
      </Avatar>

      <div className={cn(
        "flex min-w-0 max-w-[80%] flex-col gap-1.5 md:max-w-[70%]",
        isRight && "items-end"
      )}>
        <span className={cn(
          "text-xs font-medium text-muted-foreground",
          isRight ? "mr-1 text-right" : "ml-1"
        )}>
          {senderLabel}
        </span>

        <div className={cn(
          "min-w-0 max-w-full rounded-2xl border border-border px-4 py-2 bg-card",
          isRight ? "rounded-tr-none" : "rounded-tl-none bg-bubble-bot"
        )}>
          {markdown ? (
            <ChatMarkdownContent>{content}</ChatMarkdownContent>
          ) : (
            <p className="text-base leading-relaxed whitespace-pre-wrap wrap-break-word">
              {content}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
