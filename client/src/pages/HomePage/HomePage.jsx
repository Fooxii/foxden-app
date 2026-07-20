import Hero from '../../components/Hero/Hero'
import HowItWorks from '../../components/HowItWorks/HowItWorks'
import UIShowcase from '../../components/UIShowcase/UIShowcase'
import PurposeSection from '../../components/PurposeSection/PurposeSection'
import AboutSection from '../../components/AboutSection/AboutSection'
import Footer from '../../components/Footer/Footer'

export default function HomePage() {
  return (
    <div>
      <Hero />
      <HowItWorks />
      <UIShowcase />
      <PurposeSection />
      <AboutSection />
      <Footer />
    </div>
  )
}
