import React, { useEffect, useState } from 'react'
import performanceAPI from '../../services/performance'
import GoalList from '../../components/performance/GoalList'
import FeedbackForm from '../../components/performance/FeedbackForm'

const EmployeePerformance = () => {
  const [goals, setGoals] = useState([])

  const fetchGoals = async () => {
    try {
      const res = await performanceAPI.listGoals()
      setGoals(res.results || res || [])
    } catch (e) { console.error(e) }
  }

  useEffect(() => { fetchGoals() }, [])

  return (
    <div className="page performance-page">
      <div className="page-header">
        <h1>My Performance</h1>
        <p>Track your goals and send feedback</p>
      </div>

      <div className="grid">
        <section>
          <h2>My Goals</h2>
          <GoalList goals={goals} onRefresh={fetchGoals} allowEdit />
        </section>

        <aside>
          <h2>Send Feedback</h2>
          <FeedbackForm onSaved={() => {}} />
        </aside>
      </div>
    </div>
  )
}

export default EmployeePerformance
