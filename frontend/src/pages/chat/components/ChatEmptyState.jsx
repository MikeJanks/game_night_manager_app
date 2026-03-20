import ChatSuggestionChips from './ChatSuggestionChips'

const ChatEmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center text-center animate-in fade-in duration-700">
      <div className="size-20 rounded-2xl bg-surface border border-muted flex items-center justify-center mb-8">
        <span className="font-material-symbols text-slate-500 text-4xl">
          sports_esports
        </span>
      </div>
      <h2 className="text-3xl font-bold tracking-tight mb-3">
        What's the plan?
      </h2>
      <p className="text-slate-500 text-base font-normal leading-relaxed mb-10 max-w-sm">
        Start a conversation with your group or pick a suggestion below to get
        things moving.
      </p>
      <ChatSuggestionChips />
    </div>
  )
}

export default ChatEmptyState

