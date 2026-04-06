import Button from '../../../components/Button'
import IconButton from '../../../components/IconButton'
import Avatar from '../../../components/Avatar'

const ChatHeader = () => {
  return (
    <header className="flex items-center justify-between w-full border-b border-muted px-6 md:px-12 py-4 bg-surface">
      <div className="flex items-center gap-3">
        <IconButton
          variant="surface"
          size="md"
        >
          <span className="font-material-symbols text-primary text-2xl">forum</span>
        </IconButton>
        <h1 className="text-lg font-bold leading-tight tracking-tight">
          Chat
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="md"
          className="hidden md:inline-flex px-4 py-2 text-sm font-medium"
        >
          New chat
        </Button>

        <IconButton
          variant="surface"
          size="md"
          className="md:hidden"
          aria-label="New chat"
        >
          <span className="font-material-symbols text-2xl">add</span>
        </IconButton>

        <Avatar
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuDPDTnSHxAftCX1b42I9Oe6LGnuwuNOSisiIklwoCT1s2XlaEvCavfcuislOzzP9wqA-ecu479N0EHVy0_qPMus_nNhGUeU8RdXaEhkAA5zzDAmvqQA6zIU34pReXgWcQ7ptKr2xVlj8FI7YZPdIlcZBxVtmDrFjWz6u5XiVhOOAlRzgUvWrCaVMcHl82ADrlard9wmdyJOKCHpGeV2WP3us_v6FKzY6zYXRxWoU61sZf4-kmrhKLcY5MDgT5pRjnQt9st4Zt8rvUI"
          alt="User avatar"
          status="online"
        />
      </div>
    </header>
  )
}

export default ChatHeader

