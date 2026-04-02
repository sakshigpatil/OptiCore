import React, { useState } from 'react'
import performanceAPI from '../../services/performance'

const FeedbackForm = ({ onSaved = () => {} }) => {
  const [toUser, setToUser] = useState('')
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await performanceAPI.createFeedback({ to_user: toUser, message })
      setMessage('')
      onSaved()
    } catch (err) { console.error(err) }
  }

  return (
    <form className="feedback-form" onSubmit={handleSubmit}>
      <label>To (user id)</label>
      <input value={toUser} onChange={(e) => setToUser(e.target.value)} />
      <label>Message</label>
      <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
      <button className="btn" type="submit">Send</button>
    </form>
  )
}

export default FeedbackForm
