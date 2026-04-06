import IconButton from "../../../components/IconButton"
import cn from "../../../utils/cn"

const ChatMessage = ({ role, senderLabel, content }) => {
  const isUser = role === "user"

  return (
    <div className={cn("flex items-start gap-4", isUser && "flex-row-reverse")}>
      <IconButton variant="surface" size="md">
        <span className="font-material-symbols text-primary text-2xl">
          {isUser ? "person" : "smart_toy"}
        </span>
      </IconButton>

      <div className={cn("flex flex-col gap-1.5 max-w-[80%] md:max-w-[70%]", isUser && "items-end")}>
        <span className={cn("text-xs font-medium text-slate-500", isUser ? "mr-1 text-right" : "ml-1")}>
          {senderLabel}
        </span>

        <div className={cn("relative overflow-hidden rounded-2xl px-4 py-3 bg-surface border border-muted", isUser ? "rounded-tr-none" : "rounded-tl-none before:absolute before:inset-0 before:rounded-[inherit] before:bg-overlay-tint before:pointer-events-none")}>
          <p className="font-body text-base leading-relaxed">
            {content}
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
