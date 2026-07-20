import './ProfileInfo.css'

export default function ProfileInfo({ name, email, memberSince, topicCount }) {
  const initials = name ? name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase() : '?'

  return (
    <div className="profile-info">
      <div className="avatar">{initials}</div>
      <div className="profile-meta">
        <h2>{name}</h2>
        <p className="email">{email}</p>
        <p className="sub">Member since {memberSince} · {topicCount} topic{topicCount !== 1 ? 's' : ''} followed</p>
      </div>
    </div>
  )
}
