import FeatureCard from './FeatureCard'

const features = [
  {
    icon: 'sync_alt',
    title: 'Vibe-reactive',
    description:
      "Built for the group that's always down but never locks in. It grabs a time, gets the headcount, and keeps the plan tight in one place.",
    cardClassName:
      'group bg-dark-surface hover:border-primary/30 rounded-2xl border border-white/5 p-6 transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.02]',
    iconClassName:
      'bg-primary/10 text-primary flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg transition-shadow group-hover:shadow-[0_0_15px_rgba(244,37,89,0.2)]',
  },
  {
    icon: 'psychology',
    title: 'Plan stays readable',
    description:
      "No more digging through 200 messages to find the time. It keeps the details tight and easy to update so the plan doesn't get cooked by scrollback.",
    cardClassName:
      'group bg-dark-surface hover:border-accent-cyan/30 rounded-2xl border border-white/5 p-6 transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.02]',
    iconClassName:
      'bg-accent-cyan/10 text-accent-cyan flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg transition-shadow group-hover:shadow-[0_0_15px_rgba(6,182,212,0.2)]',
  },
  {
    icon: 'notifications_active',
    title: 'Squad control',
    description:
      "Ping the squad, get quick replies, and keep the headcount straight. Everyone stays locked in without you babysitting the thread.",
    cardClassName:
      'group bg-dark-surface hover:border-accent-purple/30 rounded-2xl border border-white/5 p-6 transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.02]',
    iconClassName:
      'bg-accent-purple/10 text-accent-purple flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg transition-shadow group-hover:shadow-[0_0_15px_rgba(168,85,247,0.2)]',
  },
  {
    icon: 'security',
    title: 'Privacy by design',
    description:
      "It processes messages live to help you plan, then it's done. No calendar linking. No building a chat-history profile. Just the plan, kept clean.",
    cardClassName:
      'group bg-dark-surface rounded-2xl border border-white/5 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-white/20 hover:bg-white/[0.02]',
    iconClassName:
      'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-white/5 text-white transition-shadow group-hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]',
  },
]

const FeaturesSection = () => {
  return (
    <section
      className="bg-dark-base relative overflow-hidden border-t border-white/5 px-6 py-16"
    >
      <div
        className="absolute top-0 left-0 h-full w-full opacity-50 bg-[radial-gradient(ellipse_at_top,_#0f172a,_#0a0a0c,_#0a0a0c)]"
      ></div>
      <div className="relative z-10 mx-auto max-w-[1000px]">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold text-white md:text-4xl">
            Your Personal Event Coordinator
          </h2>
          <p className="mx-auto max-w-xl text-base font-light text-slate-400">
            Focus on the game, not the logistics. We handle the boring stuff.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          {features.map((feature) => (
            <FeatureCard
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              cardClassName={feature.cardClassName}
              iconClassName={feature.iconClassName}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeaturesSection
