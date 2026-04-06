import { twMerge } from 'tailwind-merge'

const Separator = ({ orientation = 'vertical', className = '' }) => {
  const isVertical = orientation === 'vertical'
  const base = isVertical ? 'w-px h-8' : 'h-px w-full'
  const color = 'bg-muted'

  return <div className={twMerge(base, color, className)} />
}

export default Separator

