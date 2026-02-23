const Nav = () => {
  return (
    <nav
      className="bg-dark-base/80 fixed top-0 right-0 left-0 z-50 border-b border-white/5 backdrop-blur-md transition-all duration-300"
    >
      <div
        className="mx-auto flex max-w-[1200px] items-center justify-between px-6 py-4"
      >
        <div
          className="flex cursor-pointer items-center gap-3 transition-opacity hover:opacity-80"
        >
          <div
            className="from-primary to-accent-purple shadow-primary/20 flex size-8 items-center justify-center rounded-lg bg-gradient-to-br text-white shadow-lg"
          >
            <span className="font-material-symbols text-xl">casino</span>
          </div>
          <span className="text-xl font-extrabold tracking-tight text-white"
            >Game Night</span
          >
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="hidden px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:text-white sm:flex"
          >
            Log in
          </button>
          <button
            type="button"
            className="text-dark-base flex h-9 cursor-pointer items-center justify-center rounded-lg bg-white px-5 text-sm font-bold transition-all hover:bg-slate-200"
          >
            Get Started
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Nav
