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
            <h3>[ Your name ]</h3>
            <p className="about-role">[ Role / course context ]</p>
            <p className="about-bio">
              [ Placeholder bio. A few sentences about who you are, why you
              built FoxDen, and anything else you want visitors to know. ]
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
