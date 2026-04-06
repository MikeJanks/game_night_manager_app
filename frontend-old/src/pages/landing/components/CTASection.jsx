const CTASection = () => {
  return (
    <section
      className="bg-dark-base relative overflow-hidden border-t border-white/5 px-6 py-20 text-center"
    >
      <div
        className="bg-primary/10 pointer-events-none absolute top-1/2 left-1/2 h-[400px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[100px]"
      ></div>
      <div
        className="relative z-10 mx-auto flex max-w-[800px] flex-col items-center gap-8"
      >
        <h2 className="text-4xl font-bold tracking-tight text-white md:text-5xl">
          Ready to lock in?
        </h2>
        <p className="max-w-xl text-lg font-light text-slate-400">
          Don't let the hype die in the thread. Lock the time, confirm who's in,
          and run it.
        </p>
        <div className="flex w-full flex-col justify-center gap-4 sm:flex-row">
          <button
            className="text-dark-base flex h-14 items-center justify-center gap-2 rounded-lg bg-white px-10 text-lg font-bold transition-all hover:scale-105 hover:bg-slate-200"
          >
            Add to Discord
            <span className="font-material-symbols">arrow_forward</span>
          </button>
          <button
            className="flex h-14 items-center justify-center gap-2 rounded-lg border border-white/20 bg-transparent px-10 text-lg font-bold text-white transition-all hover:scale-105 hover:bg-white/5"
          >
            Try the Web Chat
          </button>
        </div>
      </div>
    </section>
  )
}

export default CTASection
