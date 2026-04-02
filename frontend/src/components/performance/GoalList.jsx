import React from 'react'
import performanceAPI from '../../services/performance'

const GoalList = ({ goals = [], onRefresh = () => {}, allowEdit = false }) => {
  const handleProgress = async (goal) => {
    const newProgress = Math.min(100, (goal.progress || 0) + 10)
    try {
      await performanceAPI.updateGoalProgress(goal.id, { progress: newProgress, note: 'Progress update' })
      onRefresh()
    } catch (e) { console.error(e) }
  }

  return (
    <div className="goal-list">
      {goals.length === 0 ? (
        <div className="empty">No goals found.</div>
      ) : (
        <ul>
          {goals.map((g) => (
            <li key={g.id} className="goal-item">
              <div className="goal-title">{g.title}</div>
              <div className="goal-meta">Owner: {g.owner || g.owner_name || '—'}</div>
              <div className="goal-progress">Progress: {g.progress || 0}%</div>
              <div className="goal-actions">
                <button onClick={() => handleProgress(g)} className="btn small">+10%</button>
                {allowEdit && <button className="btn small">Edit</button>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default GoalList
