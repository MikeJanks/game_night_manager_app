import AppPageHeader from "@/components/AppPageHeader"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

const ChatHeader = () => {
  return (
    <AppPageHeader title="Chat" icon="forum">
      {/* New chat (desktop) */}
      <Button
        variant="outline"
        size="sm"
        className="hidden md:inline-flex px-4 py-2 text-sm font-medium border-border bg-card hover:bg-muted"
      >
        New chat
      </Button>

      {/* New chat (mobile icon only) */}
      <Button
        variant="outline"
        size="icon"
        className="md:hidden h-10 w-10 border-border bg-card hover:bg-card/80"
        aria-label="New chat"
      >
        <span className="font-material-symbols text-xl">add</span>
      </Button>

      {/* Avatar */}
      <Avatar className="h-10 w-10 border border-border bg-card">
        <AvatarFallback className="bg-transparent text-primary">
          <span className="font-material-symbols text-primary text-xl">person</span>
        </AvatarFallback>
      </Avatar>
    </AppPageHeader>
  )
}

export default ChatHeader
