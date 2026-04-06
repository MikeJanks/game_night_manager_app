import { twMerge } from 'tailwind-merge'

const Chip = ({ className = '', children, as: Component = 'button', ...props }) => {
  const base =
    'inline-flex items-center gap-2 rounded-xl border border-muted bg-surface/40 px-4 py-1.5 text-sm font-medium transition-colors hover:bg-white/5'

  return (
    <Component className={twMerge(base, className)} {...props}>
      {children}
    </Component>
  )
}

export default Chip

