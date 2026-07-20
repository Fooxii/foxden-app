import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { getUserProfile } from '../../services/userService'
import { getUserFollowedTags, getUserCreatedTags } from '../../services/tagService'
import ProfileInfo from '../../components/ProfileInfo/ProfileInfo'
import TagList from '../../components/TagList/TagList'
import TagCreationModal from '../../components/TagCreationModal/TagCreationModal'
import AccountSettings from '../../components/AccountSettings/AccountSettings'
import './ProfilePage.css'

export default function ProfilePage() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [followedTags, setFollowedTags] = useState([])
  const [createdTags, setCreatedTags] = useState([])
  const [showModal, setShowModal] = useState(false)

  const load = async () => {
    if (!user) return
    const [profileData, followed, created] = await Promise.all([
      getUserProfile(user.id),
      getUserFollowedTags(user.id),
      getUserCreatedTags(user.id)
    ])
    setProfile(profileData)
    setFollowedTags(followed)
    setCreatedTags(created)
  }

  useEffect(() => { load() }, [user])

  if (!user || !profile) return null

  const memberSince = profile.member_since
    ? new Date(profile.member_since).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : '—'

  return (
    <div className="page-wrapper profile-page">
      <ProfileInfo name={profile.name} email={profile.email} memberSince={memberSince} topicCount={followedTags.length} />

      <div className="profile-section">
        <div className="section-header">
          <h3>Followed topics</h3>
          <button className="btn-ghost small" onClick={() => setShowModal(true)}>+ Create custom tag</button>
        </div>
        {followedTags.length === 0 ? (
          <p className="empty-note">You're not following any topics yet. Head to your feed to browse and follow some.</p>
        ) : (
          <TagList tags={followedTags.map((t) => t.name)} />
        )}
      </div>

      <AccountSettings customTags={createdTags} onTagDeleted={load} />

      {showModal && <TagCreationModal userId={user.id} onClose={() => setShowModal(false)} onCreated={load} />}
    </div>
  )
}
