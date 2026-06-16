export default function ProfileInfo( { name, email, memberSince } ) {
  return (
    <div className='profile-info'>
      <h2>{name}</h2>
      <h5>{email}</h5>
      <p>Member since {memberSince}</p>
    </div>
  )
}
