import { Link } from 'react-router-dom'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="landing-section-inner footer-inner">
        <div className="footer-brand"><span className="footer-dot" /><span>FoxDen</span></div>
        <nav className="footer-links">
          <Link to="/">Home</Link>
          <Link to="/feed">Feed</Link>
          <Link to="/signup">Sign up</Link>
          <Link to="/login">Log in</Link>
        </nav>
        {/* TEMPLATE ONLY — edit this line as you like */}
        <p className="footer-copy">© {new Date().getFullYear()} FoxDen. Built as a student project.</p>
      </div>
    </footer>
  )
}
