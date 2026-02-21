const badges = [
  { icon: 'lock', label: 'Private' },
  { icon: 'horizontal_rule', label: 'No Logging' },
  { icon: 'terminal', label: 'Zero Commands' },
  { icon: 'bolt', label: 'Seamless' },
]

const TrustBadges = () => {
  return (
    <div className="mt-6 flex flex-wrap gap-4" data-purpose="trust-badges">
      <div className="mt-2 flex flex-wrap items-center gap-x-6 gap-y-2 opacity-60">
        {badges.map(({ icon, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[12px] text-slate-500">
              {icon}
            </span>
            <span className="text-[10px] font-medium tracking-[0.15em] text-slate-500 uppercase">
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TrustBadges
