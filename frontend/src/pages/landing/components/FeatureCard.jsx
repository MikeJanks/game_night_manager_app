const FeatureCard = ({
  icon,
  title,
  description,
  cardClassName = 'group bg-dark-surface hover:border-primary/30 rounded-2xl border border-white/5 p-6 transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.02]',
  iconClassName = 'bg-primary/10 text-primary flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg transition-shadow group-hover:shadow-[0_0_15px_rgba(244,37,89,0.2)]',
}) => {
  return (
    <div className={cardClassName}>
      <div className="flex items-start gap-4">
        <div className={iconClassName}>
          <span className="material-symbols-outlined text-xl">{icon}</span>
        </div>
        <div>
          <h3 className="mb-2 text-base font-bold text-white">
            {title}
          </h3>
          <p className="text-sm leading-relaxed text-slate-400">
            {description}
          </p>
        </div>
      </div>
    </div>
  )
}

export default FeatureCard
