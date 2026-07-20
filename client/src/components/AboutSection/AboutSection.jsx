import './AboutSection.css'

// TEMPLATE ONLY — replace name, role, bio, and avatar initial below
export default function AboutSection() {
  return (
    <section className="landing-section about-section">
      <div className="landing-section-inner about-inner">
        <p className="section-label">Who built this</p>
        <div className="about-card">
          <div className="about-avatar">?</div>
          <div className="about-text">
            <h3>[ Natanael Ortiz Lugo ]</h3>
            <p className="about-role">[ FullStack Developer ]</p>
            <p className="about-bio">
               Passionate about all things tech, whether it's gaming, hardware or programming 
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
