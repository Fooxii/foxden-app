import './AboutSection.css'
import studentImg from '../../assets/me.jpg'

export default function AboutSection() {
  return (
    <section className="landing-section about-section">
      <div className="landing-section-inner about-inner">
        <p className="section-label">[ Built by ]</p>
        <div className="about-card">
          <img src={studentImg} alt="Natanael Ortiz Lugo" className="about-avatar" />
          <div className="about-text">
            <h3>Natanael Ortiz Lugo</h3>
            <p className="about-role">[ FullStack Developer ]</p>
            <p className="about-bio">
              Student at Holberton Coding School (Puerto Rico)
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
