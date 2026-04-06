import { cn } from "@/lib/utils"

export function AmbientBlobBackground({ className }) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 z-0 overflow-hidden",
        className
      )}
    >
      <div className="bg-primary/10 absolute top-[-10%] left-[-10%] h-[50%] w-[50%] rounded-full blur-[120px]" />
      <div className="bg-accent-purple/10 absolute right-[-10%] bottom-[-10%] h-[40%] w-[40%] rounded-full blur-[100px]" />
      <div className="bg-accent-cyan/5 absolute top-[20%] right-[20%] h-[30%] w-[30%] rounded-full blur-[80px]" />
    </div>
  )
}

export default AmbientBlobBackground
