import './HowItWorks.css'

const steps = [
  {
    num: '01',
    title: 'Follow your topics',
    text: 'Pick from official tags or create your own — as specific as a single game or as broad as an entire industry.',
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M12 2l3 6 6 .9-4.5 4.3 1 6.3L12 16.5 6.5 19.5l1-6.3L3 8.9 9 8z"/></svg>
  },
  {
    num: '02',
    title: 'We scan the sources',
    text: 'Our pipeline continuously pulls from trusted outlets and matches new articles to your interests using semantic search.',
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16" y2="16"/></svg>
  },
  {
    num: '03',
    title: 'Get your feed',
    text: 'Open FoxDen to a feed built entirely around what you actually follow — nothing else.',
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4"><rect x="3" y="4" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
  }
]

export default function HowItWorks() {
  return (
    <section className="landing-section how-it-works-wrap">
      <div className="steps-row">
        {steps.map((step) => (
          <div className="how-it-works-step" key={step.num}>
            <div className="step-card-large">
              <div className="step-icon-large">{step.icon}</div>
              <span className="step-num-large">{step.num}</span>
              <h2 className="step-title-large">{step.title}</h2>
              <p className="step-text-large">{step.text}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
