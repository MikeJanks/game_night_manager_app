import { Link } from "react-router-dom"

const Nav = () => {
  return (
    <nav className="bg-background/80 fixed top-0 right-0 left-0 z-50 border-b border-white/5 backdrop-blur-md transition-all duration-300">
      <div className="mx-auto flex max-w-[1200px] items-center justify-between px-6 py-4">
        <Link
          to="/"
          className="flex cursor-pointer items-center gap-3 transition-opacity hover:opacity-80"
        >
          <div className="from-primary to-accent-purple shadow-primary/20 flex size-8 items-center justify-center rounded-lg bg-linear-to-br text-white shadow-lg">
            <span className="font-material-symbols text-xl">
              casino
            </span>
          </div>
          <span className="text-xl font-extrabold tracking-tight text-white">
            Game Night
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="hidden px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:text-white sm:flex"
          >
            Log in
          </Link>
          <Link
            to="/signup"
            className="text-background flex h-9 cursor-pointer items-center justify-center rounded-lg bg-white px-5 text-sm font-bold transition-all hover:bg-slate-200"
          >
            Sign up
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Nav
