import { twMerge } from 'tailwind-merge'

const TextField = ({
  className = '',
  type = 'text',
  ...props
}) => {
  const base =
    'w-full bg-transparent border-none text-base font-body placeholder:text-slate-500 focus:outline-none'

  return <input type={type} className={twMerge(base, className)} {...props} />
}

export default TextField

