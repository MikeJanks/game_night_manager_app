import IconButton from '../../../components/IconButton'
import TextField from '../../../components/TextField'
import Button from '../../../components/Button'

const ChatInputBar = () => {
  return (
    <footer className="relative w-full flex items-center bg-surface border border-muted rounded-2xl p-2 shadow-2xl focus-within:border-slate-700 transition-all">

      <TextField
        className="flex-1 px-3"
        placeholder="Type a message..."
      />

      <IconButton
        variant="primary"
        size="md"
        aria-label="Send message"
      >
        <span className="font-material-symbols text-2xl">send</span>
      </IconButton>
    </footer>
  )
}

export default ChatInputBar

