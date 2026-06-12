import Navbar from '../components/Navbar/Navbar'
// import FilterSection from '../components/FilterSection/FilterSection'
import NewsSection from '../components/NewsSection/NewsSection'
import TagList from '../components/TagList/TagList'
import { mockUser } from "../data/mockData.js"

export default function FeedPage() {
  return (
    <div className='page-wrapper'>
      {/* <FilterSection /> */}
      <TagList
        tags={mockUser.topics}
      />
      <NewsSection />
    </div>
  )
}
