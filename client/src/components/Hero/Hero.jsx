import './Hero.css'

export default function Hero() {
  return (
    <div className='hero'>
      <p className='highlight txt1'>PERSONALIZED NEWS</p>
      <h1>Built around your interests.</h1>
      <p className='txt2'>Keep track of topics you care about, all in one place.</p>
      <div className='button-container'>
        <button className='button1'>Get started</button>
        <button className='button2'>Browse feed</button>
      </div>
    </div>
  )
}
