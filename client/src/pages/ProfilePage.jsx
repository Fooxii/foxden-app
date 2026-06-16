import ProfileInfo from "../components/ProfileInfo/ProfileInfo";
import { mockUser } from '../data/mockData.js'
import TagList from "../components/TagList/TagList.jsx";

export default function ProfilePage() {
  return (
    <div className='page-wrapper'>
        <ProfileInfo
          name={mockUser.name}
          email={mockUser.email}
          memberSince={mockUser.memberSince}
        />
        <h3>FOLLOWED TAGS</h3>
        <TagList
          tags={mockUser.topics}
        />
        <h3>SAVED ARTICLES</h3>
    </div>
  )
}
