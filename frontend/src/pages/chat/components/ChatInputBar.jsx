import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

function ChatInputBar({value, onChange, onSend, placeholder = "Type a message...", isLoading = false}) {

  function handleSubmit(e) {
    e.preventDefault()
    const text = typeof value === "string" ? value.trim() : ""
    if (!text) return
    onSend?.(text)
  }

  return (
    <div className="flex w-full max-w-3xl flex-col">
      <form onSubmit={handleSubmit} className="w-full">
        <div className={cn(
            "flex w-full items-center gap-1 rounded-2xl border border-border bg-card p-2 shadow-2xl transition-[border-color,box-shadow]",
            "focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/30"
        )}>

          {/* Input */}
          <div className="min-w-0 flex-1 px-2">
            <Input
              name="message"
              value={value}
              onChange={(e) => onChange?.(e.target.value)}
              placeholder={placeholder}
              autoComplete="off"
              disabled={isLoading}
              className={cn(
                "h-10 border-0 bg-transparent px-0 py-0 shadow-none font-body text-[15px] focus-visible:ring-0 md:text-[15px]",
                "text-foreground placeholder:text-muted-foreground"
              )}
            />
          </div>

          {/* Submit */}
          <Button
            type="submit"
            variant="default"
            aria-label="Send message"
            className="size-10 shrink-0"
            disabled={isLoading}
          >
            <span className="font-material-symbols text-xl leading-none">send</span>
          </Button>

        </div>
      </form>
    </div>
  )
}

export default ChatInputBar
