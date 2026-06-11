import TrendingBlock from "../TrendingBlock/TrendingBlock";
import { mockTrending } from "../../data/mockData";
import './TrendingSection.css'

export default function TrendingSection() {
  return (
    <div className='trendingsection'>
      <p>TRENDING NOW</p>
      {mockTrending.map((trend) => (
        <TrendingBlock
          key={trend.id}
          source={trend.source}
          items={trend.items}
        />
      ))}
    </div>
  )
}
