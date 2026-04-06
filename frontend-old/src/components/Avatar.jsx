import { twMerge } from 'tailwind-merge'

const Avatar = ({ src, alt = '', size = 'md' }) => {
  const sizeClasses =
    size === 'sm'
      ? 'h-8 w-8'
      : size === 'lg'
        ? 'h-12 w-12'
        : 'h-10 w-10'

  return (
    <div className="relative inline-flex items-center justify-center">
      <div
        className={twMerge(
          sizeClasses,
          'rounded-full border border-muted bg-surface overflow-hidden bg-cover bg-center'
        )}
        style={src ? { backgroundImage: `url('${src}')` } : undefined}
        aria-label={alt}
      />
    </div>
  )
}

export default Avatar

