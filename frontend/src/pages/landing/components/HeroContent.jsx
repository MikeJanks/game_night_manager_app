import TrustBadges from './TrustBadges'

const HeroContent = () => {
  return (
    <div className="relative z-10 flex flex-col gap-8">
      <div className="flex flex-wrap gap-2">
        <div
          className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 backdrop-blur-md"
        >
          <span
            className="bg-accent-cyan flex h-1.5 w-1.5 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]"
          ></span>
          <span className="text-xs font-semibold tracking-wide text-slate-300"
            >DISCORD BOT — LIVE</span
          >
        </div>
        <div
          className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 backdrop-blur-md"
        >
          <span
            className="bg-accent-cyan flex h-1.5 w-1.5 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]"
          ></span>
          <span className="text-xs font-semibold tracking-wide text-slate-300"
            >WEB CHAT — LIVE</span
          >
        </div>
      </div>
      <h1
        className="text-5xl leading-[1] font-bold tracking-tight text-white md:text-7xl"
      >
        Stop planning. <br />
        <span
          className="bg-gradient-to-r from-slate-200 via-white to-slate-400 bg-clip-text text-transparent"
          >Start playing.</span
        >
      </h1>
      <p className="max-w-lg text-lg leading-relaxed font-light text-slate-400">
        Drop the plan in the chat. It'll lock the time, confirm the squad, and
        end the endless "wait what time?"
      </p>
      <div className="flex flex-col gap-4 pt-4 sm:flex-row">
        <button
          className="group bg-primary relative flex h-12 items-center justify-center gap-2 overflow-hidden rounded-lg px-8 text-base font-semibold text-white transition-all hover:shadow-[0_0_20px_rgba(244,37,89,0.4)]"
        >
          <div
            className="absolute inset-0 translate-y-full bg-white/20 transition-transform duration-300 group-hover:translate-y-0"
          ></div>
          <span className="relative z-10 flex items-center gap-2">
            Add to Discord
            <span className="font-material-symbols text-sm"
              >arrow_forward</span
            >
          </span>
        </button>
        <button
          className="flex h-12 items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-8 text-base font-semibold text-white backdrop-blur-sm transition-all hover:bg-white/10"
        >
          Try the Web Chat
        </button>
      </div>
      <TrustBadges />
    </div>
  )
}

export default HeroContent
