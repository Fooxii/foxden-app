import feedImg from '../../assets/feedSample.png'
import signupImg from '../../assets/signupSample.png'
import tagImg from '../../assets/tagcreationSample.png'
import './UIShowcase.css'

const showcaseItems = [
  { label: 'Signup Page', heading: 'Create Account', body: 'Signup to start using FoxDen', image: signupImg },
  { label: 'Custom Tags', heading: 'Add Custom Tags', body: 'Create your own tags to personalize your experience', image: tagImg },
  { label: 'Feed Page', heading: 'Personalized Feed', body: 'Enjoy news picked just for you', image: feedImg },
]

export default function UIShowcase() {
  return (
    <div className="ui-showcase-wrap">
      {showcaseItems.map((item, i) => (
        <section className="landing-section split-section" key={item.label}>
          <div className={`landing-section-inner split-inner ${i % 2 === 1 ? 'reverse-on-desktop' : ''}`}>
            <div className="split-text">
              {i === 0 && <p className="section-label">See it in action</p>}
              <h2 className="section-heading">{item.heading}</h2>
              <p className="split-body">{item.body}</p>
            </div>
            <div className="split-visual">
              <div className="showcase-frame">
                <div className="showcase-chrome"><span className="chrome-dot" /><span className="chrome-dot" /><span className="chrome-dot" /></div>
                <div className="showcase-placeholder">
                  <img src={item.image} alt={`${item.label} screenshot`} className="showcase-img" />
                </div>
              </div>
            </div>
          </div>
        </section>
      ))}
    </div>
  )
}
