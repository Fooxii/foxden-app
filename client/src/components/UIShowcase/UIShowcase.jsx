import './UIShowcase.css'

// TEMPLATE ONLY — replace each heading/body and swap the placeholder
// frame's contents for a real screenshot
const showcaseItems = [
  { label: 'Feed Page', heading: '[ Placeholder — feed page description ]', body: '[ Placeholder — a sentence or two about the feed. ]' },
  { label: 'Custom Tags', heading: '[ Placeholder — custom tags description ]', body: '[ Placeholder — a sentence or two about custom tags. ]' },
  { label: 'Story Clusters', heading: '[ Placeholder — story clusters description ]', body: '[ Placeholder — a sentence or two about clustering. ]' },
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
                <div className="showcase-placeholder"><span>Drop {item.label} screenshot here</span></div>
              </div>
            </div>
          </div>
        </section>
      ))}
    </div>
  )
}
