import Chip from '../../../components/Chip'

const ChatSuggestionChips = () => {
  return (
    <div className="flex flex-wrap justify-center gap-3 mb-12">
      <Chip>
        <span className="font-material-symbols text-slate-500 text-lg">
          calendar_today
        </span>
        <span>Schedule RPG</span>
      </Chip>

      <Chip>
        <span className="font-material-symbols text-slate-500 text-lg">
          casino
        </span>
        <span>Board Game Night</span>
      </Chip>

      <Chip>
        <span className="font-material-symbols text-slate-500 text-lg">
          person_add
        </span>
        <span>Invite Players</span>
      </Chip>
    </div>
  )
}

export default ChatSuggestionChips

