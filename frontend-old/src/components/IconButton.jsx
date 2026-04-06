import { twMerge } from 'tailwind-merge'

const baseClasses =
  'inline-flex items-center justify-center font-body rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-canvas disabled:opacity-50 disabled:cursor-not-allowed'

const variantClasses = {
  surface:
    'bg-surface border border-muted hover:bg-white/5',
  ghost:
    'bg-transparent border border-transparent hover:bg-surface/60',
  primary: 'bg-primary hover:opacity-90',
}

const sizeClasses = {
  sm: 'h-9 w-9 text-sm',
  md: 'h-10 w-10 text-base',
}

const IconButton = ({
  variant = 'surface',
  size = 'md',
  className = '',
  children,
  type = 'button',
  ...props
}) => {
  const variantClass = variantClasses[variant] ?? variantClasses.surface
  const sizeClass = sizeClasses[size] ?? sizeClasses.md

  return (
    <button
      type={type}
      className={twMerge(baseClasses, variantClass, sizeClass, className)}
      {...props}
    >
      {children}
    </button>
  )
}

export default IconButton

