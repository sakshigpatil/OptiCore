import React, { useEffect, useState } from 'react'
import performanceAPI from '../../services/performance'
import GoalList from '../../components/performance/GoalList'
import ReviewList from '../../components/performance/ReviewList'

const ManagerPerformance = () => {
  const [goals, setGoals] = useState([])
  const [reviews, setReviews] = useState([])

  const fetchData = async () => {
    try {
      const g = await performanceAPI.listGoals()
      const r = await performanceAPI.listReviews()
      setGoals(g.results || g || [])
      setReviews(r.results || r || [])
    } catch (e) {
      console.error('Error fetching performance data', e)
    }
  }

  useEffect(() => { fetchData() }, [])

  return (
    <div className="page performance-page">
      <div className="page-header">
        <h1>Performance Management</h1>
        <p>Goals, reviews and feedback for your team</p>
      </div>

      <div className="grid two-column">
        <section>
          <h2>Team Goals</h2>
          <GoalList goals={goals} onRefresh={fetchData} />
        </section>

        <section>
          <h2>Reviews</h2>
          <ReviewList reviews={reviews} onRefresh={fetchData} />
        </section>
      </div>
    </div>
  )
}

export default ManagerPerformance
