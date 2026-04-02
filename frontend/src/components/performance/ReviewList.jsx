import React from 'react'
import performanceAPI from '../../services/performance'

const ReviewList = ({ reviews = [], onRefresh = () => {} }) => {
  const handleApprove = async (id) => {
    try {
      await performanceAPI.approveReview(id)
      onRefresh()
    } catch (e) { console.error(e) }
  }

  const handleReject = async (id) => {
    try {
      await performanceAPI.rejectReview(id, { reason: 'Needs more details' })
      onRefresh()
    } catch (e) { console.error(e) }
  }

  return (
    <div className="review-list">
      {reviews.length === 0 ? (
        <div className="empty">No reviews yet.</div>
      ) : (
        <ul>
          {reviews.map(r => (
            <li key={r.id} className="review-item">
              <div className="review-meta">Employee: {r.employee || r.employee_name || '—'}</div>
              <div className="review-rating">Rating: {r.rating || '—'}</div>
              <div className="review-comments">{r.comments}</div>
              <div className="review-actions">
                <button onClick={() => handleApprove(r.id)} className="btn small success">Approve</button>
                <button onClick={() => handleReject(r.id)} className="btn small danger">Reject</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default ReviewList
