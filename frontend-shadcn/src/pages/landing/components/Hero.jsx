import AmbientBlobBackground from '@/components/AmbientBlobBackground'
import HeroContent from './HeroContent'
import DiscordMockup from './DiscordMockup'

const Hero = () => {
  return (
    <header
      className="relative flex min-h-screen items-center overflow-hidden pt-32 pb-20 lg:pt-48 lg:pb-32"
    >
      <AmbientBlobBackground />
      <div
        className="relative z-10 mx-auto grid max-w-[1200px] grid-cols-1 items-center gap-16 px-6 lg:grid-cols-2"
      >
        <HeroContent />
        <DiscordMockup />
      </div>
    </header>
  )
}

export default Hero
