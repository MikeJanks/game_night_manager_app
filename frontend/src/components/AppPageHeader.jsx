import { cn } from "@/lib/utils"

function AppPageHeader({ title, icon, children, className }) {
  return (
    <header
      className={cn(
        "h-16 flex items-center justify-between border-b border-border bg-card px-6",
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* <div className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-card"> */}
          <span
            className="font-material-symbols text-primary text-xl"
            aria-hidden
          >
            {icon}
          </span>
        {/* </div> */}
        <h1 className="text-lg font-bold leading-tight tracking-tight">
          {title}
        </h1>
      </div>

      {children != null ? (
        <div className="flex items-center gap-4">{children}</div>
      ) : null}
    </header>
  )
}

export default AppPageHeader
