import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"

const ChatHeader = () => {
  return (
    <header className="flex items-center justify-between border-b border-border bg-card px-6 py-4">
      {/* Left: icon + title */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-card border border-border">
          <span className="font-material-symbols text-primary text-xl">forum</span>
        </div>
        <h1 className="text-lg font-bold leading-tight tracking-tight">
          Chat
        </h1>
      </div>

      {/* Right: new chat + avatar */}
      <div className="flex items-center gap-4">
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
          {/* <AvatarImage
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuD8G-ZVPxXeRXj1JaiUSIpa5ypyO1Vcy4YgMVh8b2nCu8lGwqNYTkzVMHvQF2eEJ7qfXqL_RJemU31850g172NIM-hfsUw7onsTQoosF_qRPYc5mNtBwnizBBq2kJCfoEV2cNd7f-5n6h7eht3iL0D1QFiL2JTBIsgSZRF1l8zt0VeDcIdJJyXmambuVIq1mzXn1C0pLwnIcVEkO4Id4-GjKSzqFuSjhAMZBaYBnAVkmsOGfrirNkZUT5BTOzp2LpiaPh3UpkGtBf0"
            alt="User avatar"
          /> */}
          <AvatarFallback className="bg-transparent text-primary">
            <span className="font-material-symbols text-primary text-xl">person</span>
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  )
}

export default ChatHeader