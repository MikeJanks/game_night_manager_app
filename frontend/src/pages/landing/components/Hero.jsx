import HeroContent from './HeroContent'
import DiscordMockup from './DiscordMockup'

const Hero = () => {
  return (
    <header
      className="relative flex min-h-screen items-center overflow-hidden pt-32 pb-20 lg:pt-48 lg:pb-32"
    >
      <div
        className="pointer-events-none absolute top-0 left-0 z-10 h-full w-full overflow-hidden"
      >
        <div
          className="bg-primary/10 absolute top-[-10%] left-[-10%] h-[50%] w-[50%] rounded-full blur-[120px]"
        ></div>
        <div
          className="bg-accent-purple/10 absolute right-[-10%] bottom-[-10%] h-[40%] w-[40%] rounded-full blur-[100px]"
        ></div>
        <div
          className="bg-accent-cyan/5 absolute top-[20%] right-[20%] h-[30%] w-[30%] rounded-full blur-[80px]"
        ></div>
      </div>
      <div
        className="mx-auto grid max-w-[1200px] grid-cols-1 items-center gap-16 px-6 lg:grid-cols-2"
      >
        <HeroContent />
        <DiscordMockup />
      </div>
    </header>
  )
}

export default Hero
