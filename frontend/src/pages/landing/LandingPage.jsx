import Nav from './components/Nav'
import Hero from './components/Hero'
import FeaturesSection from './components/FeaturesSection'
import CTASection from './components/CTASection'
import Footer from './components/Footer'

const LandingPage = () => {
  return (
    <div className="bg-background overflow-x-hidden text-slate-200">
      <Nav />
      <Hero />
      <FeaturesSection />
      <CTASection />
      <Footer />
    </div>
  )
}

export default LandingPage
