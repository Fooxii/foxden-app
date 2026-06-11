import Hero from "../components/Hero/Hero";
import Navbar from "../components/Navbar/Navbar";
import TrendingSection from "../components/TrendingSection/TrendingSection";

export default function Homepage() {
  return(
    <div className='page-wrapper'>
      <Hero />
      <TrendingSection />
    </div>
  )
}
