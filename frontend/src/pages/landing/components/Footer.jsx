const Footer = () => {
  return (
    <footer className="bg-dark-surface border-t border-white/5 py-8">
      <div className="mx-auto max-w-[1200px] px-6">
        <div
          className="flex flex-col items-center justify-between gap-6 md:flex-row"
        >
          <div className="flex items-center gap-2 text-white">
            <div
              className="from-primary to-accent-purple flex size-6 items-center justify-center rounded bg-gradient-to-br text-xs text-white shadow-lg"
            >
              <span className="font-material-symbols text-[14px]">
                casino
              </span>
            </div>
            <span className="text-lg font-bold">Game Night</span>
          </div>
          <p className="text-sm text-slate-600">
            © 2026 Game Night Manager. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
