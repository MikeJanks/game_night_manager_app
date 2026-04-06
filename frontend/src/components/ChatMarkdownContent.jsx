import { cn } from "@/lib/utils"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

const markdownComponents = {
  pre({ children, ...props }) {
    return (
      <div className="my-3 max-w-full overflow-x-auto rounded-md border border-border bg-muted/40">
        <pre {...props} className="mb-0 max-w-full overflow-x-auto p-3 text-sm bg-transparent!">
          {children}
        </pre>
      </div>
    )
  },
  table({ children, ...props }) {
    return (
      <div className="my-3 w-full max-w-full overflow-x-auto">
        <table {...props}>{children}</table>
      </div>
    )
  },
}

/** Dark-only UI: prose-invert keeps headings/emphasis readable (no Tailwind `dark` class on root). */
export function ChatMarkdownContent({ className, children }) {
  return (
    <div
      className={cn(
        "prose prose-sm prose-invert max-w-none min-w-0 text-foreground",
        "wrap-break-word prose-headings:font-display prose-p:my-2 prose-p:leading-relaxed",
        "prose-code:rounded prose-code:bg-muted/60 prose-code:px-1 prose-code:py-0.5 prose-code:before:content-none prose-code:after:content-none",
        "prose-pre:p-0 prose-pre:bg-transparent prose-pre:border-0 prose-pre:shadow-none",
        "prose-a:text-primary prose-a:no-underline hover:prose-a:underline",
        "prose-li:my-0.5",
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
        {children}
      </ReactMarkdown>
    </div>
  )
}
