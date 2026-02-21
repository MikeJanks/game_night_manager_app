const DiscordMockup = () => {
  return (
    <div
      className="perspective-container relative z-0 flex h-[500px] w-full items-center justify-center lg:ml-12"
    >
      <div
        className="glass-panel rotate-3d relative z-20 flex w-[400px] flex-col overflow-hidden rounded-xl shadow-2xl"
      >
        <div
          className="flex items-center justify-between border-b border-white/5 bg-black/20 p-3"
        >
          <div className="flex items-center gap-2">
            <div className="h-5 w-5 text-slate-400">
              <span className="material-symbols-outlined text-lg">tag</span>
            </div>
            <span className="text-sm font-bold tracking-tight text-white"
              >scheduling</span
            >
          </div>
          <div className="flex items-center gap-3 text-slate-400">
            <span
              className="material-symbols-outlined cursor-pointer text-lg hover:text-white"
              >notifications</span
            >
            <span
              className="material-symbols-outlined cursor-pointer text-lg hover:text-white"
              >people</span
            >
            <div
              className="flex h-6 w-48 items-center rounded bg-black/30 px-2 text-[10px] text-slate-500"
            >
              Search
            </div>
          </div>
        </div>
        <div
          className="flex flex-1 flex-col justify-end space-y-4 bg-gradient-to-b from-transparent to-black/10 p-4"
        >
          <div className="group flex gap-3">
            <div
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-indigo-500 text-xs font-bold text-white shadow-lg"
            >
              DM
            </div>
            <div className="flex-1">
              <div className="flex items-baseline gap-2">
                <span
                  className="cursor-pointer text-sm font-medium text-white hover:underline"
                  >DungeonMaster</span
                >
                <span className="text-[10px] text-slate-400"
                  >Today at 8:29 PM</span
                >
              </div>
              <div className="mt-0.5 text-sm text-slate-200">
                anyone down for DnD Friday?
              </div>
            </div>
          </div>
          <div className="mt-1 flex gap-3">
            <div
              className="from-primary to-accent-purple shadow-primary/20 mt-0.5 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br shadow-lg"
            >
              <span className="material-symbols-outlined text-sm text-white"
                >smart_toy</span
              >
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span
                  className="flex items-center gap-1 text-sm font-medium text-white"
                >
                  Game Night Bot
                  <span
                    className="bg-primary rounded-[3px] px-1 py-[1px] text-[9px] font-bold tracking-wide text-white uppercase"
                    >BOT</span
                  >
                </span>
                <span className="text-[10px] text-slate-400"
                  >Today at 8:29 PM</span
                >
              </div>
              <div className="mt-0.5 text-sm text-slate-200">
                Want me to lock that in?
              </div>
              <div
                className="border-primary mt-1.5 max-w-[95%] rounded-r-md border-l-4 bg-black/20 p-3"
              >
                <div className="mb-2 flex items-center gap-2">
                  <div
                    className="h-4 w-4 animate-pulse rounded-full bg-green-500"
                  ></div>
                  <span className="text-xs font-bold text-white"
                    >DnD session 4</span
                  >
                </div>
                <div
                  className="mb-3 flex items-center gap-3 rounded border border-white/5 bg-white/5 p-2"
                >
                  <div className="rounded bg-white/10 p-1.5 text-white">
                    <span className="material-symbols-outlined text-lg"
                      >calendar_month</span
                    >
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">
                      Friday, Nov 24
                    </div>
                    <div className="text-[10px] text-slate-400">
                      7:00 PM EST
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    className="bg-primary hover:bg-primary-glow shadow-primary/20 rounded px-3 py-1.5 text-[10px] font-bold text-white shadow-lg transition-colors"
                  >
                    Accept
                  </button>
                  <button
                    className="rounded border border-white/10 bg-white/5 px-3 py-1.5 text-[10px] font-bold text-slate-300 transition-colors hover:bg-white/10"
                  >
                    Suggest Other
                  </button>
                </div>
                <div className="mt-2 text-[9px] text-slate-500">
                  <span className="text-green-400">3</span> confirmed
                </div>
              </div>
            </div>
          </div>
        </div>
        <div
          className="m-2 flex items-center gap-3 rounded-lg border-t border-white/5 bg-black/10 p-3"
        >
          <div
            className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-500"
          >
            <span
              className="material-symbols-outlined text-[14px] font-bold text-black"
              >add</span
            >
          </div>
          <div className="flex-1 text-xs font-medium text-slate-500">
            Message #scheduling
          </div>
          <div className="flex gap-2 text-slate-400">
            <span className="material-symbols-outlined text-lg">gif_box</span>
            <span className="material-symbols-outlined text-lg"
              >sentiment_satisfied</span
            >
          </div>
        </div>
      </div>
      <div
        className="from-accent-purple/20 border-accent-purple/20 floating-shard-delayed absolute top-12 -right-8 -z-10 h-24 w-24 rotate-[15deg] transform rounded-xl border bg-gradient-to-br to-transparent backdrop-blur-md"
      ></div>
      <div
        className="from-accent-cyan/20 border-accent-cyan/20 floating-shard absolute bottom-16 -left-6 -z-10 h-16 w-16 -rotate-[10deg] transform rounded-lg border bg-gradient-to-tl to-transparent backdrop-blur-md"
      ></div>
      <div
        className="pointer-events-none absolute top-1/4 right-0 z-0 h-[1px] w-[120%] -rotate-12 transform bg-gradient-to-r from-transparent via-white/5 to-transparent"
      ></div>
    </div>
  )
}

export default DiscordMockup
