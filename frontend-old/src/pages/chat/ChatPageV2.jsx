import ChatHeader from './components/ChatHeader'
import ChatMain from './components/ChatMain'
import ChatInputBar from './components/ChatInputBar'

const ChatPageV2 = () => {
  return (
    <div className="flex-1 flex h-dvh w-full flex-col items-center bg-canvas text-slate-100">
      <ChatHeader />
      <div className='flex-1 flex flex-col max-w-3xl w-full pb-4 px-4 overflow-hidden'>
        <ChatMain />
        <ChatInputBar />
      </div>
    </div>
  )
}

export default ChatPageV2

