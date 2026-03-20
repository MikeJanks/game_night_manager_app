import { twMerge } from 'tailwind-merge'

const baseClasses = 'inline-flex items-center justify-center font-body font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-canvas disabled:opacity-50 disabled:cursor-not-allowed'

const variantClasses = {
  primary: 'bg-primary hover:opacity-90',
  ghost: 'bg-surface border border-muted hover:bg-white/5',
  outline: 'bg-transparent border border-muted hover:bg-surface/60',
}

const sizeClasses = {
  sm: 'h-9 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
}

const Button = ({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  type = 'button',
  ...props
}) => {
  const variantClass = variantClasses[variant] ?? variantClasses.primary
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

export default Button

