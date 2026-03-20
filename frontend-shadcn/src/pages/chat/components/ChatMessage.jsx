import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { getInitials } from "@/lib/getInitials"
import { cn } from "@/lib/utils"

const ChatMessage = ({ side = "left", senderLabel, content, avatar }) => {
  const isRight = side === "right"
  const avatarFallback = getInitials(senderLabel)

  return (
    <div className={cn("flex items-start gap-4", isRight && "flex-row-reverse")}>
      <Avatar size="lg" className="border border-border bg-card">
        {avatar 
          ? avatar // <AvatarImage src={avatarSrc} alt={senderLabel} />
          : <AvatarFallback className="bg-transparent text-primary">{avatarFallback}</AvatarFallback>
        }
      </Avatar>

      <div className={cn(
        "flex flex-col gap-1.5 max-w-[80%] md:max-w-[70%]",
        isRight && "items-end"
      )}>
        <span className={cn(
          "text-xs font-medium text-muted-foreground",
          isRight ? "mr-1 text-right" : "ml-1"
        )}>
          {senderLabel}
        </span>

        <div className={cn(
          "rounded-2xl border border-border px-5 py-3.5 bg-card",
          isRight ? "rounded-tr-none" : "rounded-tl-none bg-bubble-bot"
        )}>
          <p className="text-base leading-relaxed whitespace-pre-wrap wrap-break-word">
            {content}
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage

