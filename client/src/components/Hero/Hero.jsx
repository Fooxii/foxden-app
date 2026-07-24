import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './Hero.css'

export default function Hero() {
  const navigate = useNavigate()
  const { user } = useAuth()

  return (
    <section className="landing-section hero-section">
      <div className="landing-section-inner hero-inner">
        <img
          src="/FoxDenLogo.png"
          alt="FoxDen"
          className="hero-logo"
        />
        <div className="hero-eyebrow">Personalized news</div>
        <h1>Built around <em>your</em> interests.</h1>
        <p className="hero-lead">Keep track of topics you care about, all in one place — from broad categories down to the single game, team, or company you follow closest.</p>
        <div className="hero-actions">
          <button
            className="btn-primary"
            onClick={() => navigate(user ? '/feed' : '/signup')}
          >
            Get started
          </button>
          <button className="btn-ghost" onClick={() => navigate('/feed')}>Browse feed</button>
        </div>
      </div>
    </section>
  )
}
