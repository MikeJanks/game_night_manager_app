import { Button } from "@/components/ui/button"

const ChatEmptyState = () => {
  return (
    <div className="flex flex-1 flex-col items-center justify-center text-center px-4 py-10">
      <div className="mb-8 flex size-20 items-center justify-center rounded-2xl border border-border bg-card">
        <span className="font-material-symbols text-4xl">
          sports_esports
        </span>
      </div>

      <h2 className="mb-3 text-3xl font-bold tracking-tight">What's the plan?</h2>
      <p className="mb-10 max-w-sm text-base leading-relaxed">
        Start a conversation with your group or pick a suggestion below to get
        things moving.
      </p>

      <div className="flex flex-wrap justify-center gap-3">
        <Button type="button" variant="secondary" className="gap-2">
          <span className="font-material-symbols text-lg">
            calendar_today
          </span>
          Schedule RPG
        </Button>

        <Button type="button" variant="secondary" className="gap-2">
          <span className="font-material-symbols text-lg">
            casino
          </span>
          Board Game Night
        </Button>

        <Button type="button" variant="secondary" className="gap-2">
          <span className="font-material-symbols text-lg">
            person_add
          </span>
          Invite Players
        </Button>
      </div>
    </div>
  )
}

export default ChatEmptyState

