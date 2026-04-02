import api from './api'

const performanceAPI = {
  // Goals
  listGoals: () => api.get('/performance/goals/'),
  createGoal: (data) => api.post('/performance/goals/', data),
  updateGoal: (id, data) => api.put(`/performance/goals/${id}/`, data),
  updateGoalProgress: (id, data) => api.post(`/performance/goals/${id}/update_progress/`, data),

  // Reviews
  listReviews: () => api.get('/performance/reviews/'),
  createReview: (data) => api.post('/performance/reviews/', data),
  submitReview: (id) => api.post(`/performance/reviews/${id}/submit/`),
  approveReview: (id) => api.post(`/performance/reviews/${id}/approve/`),
  rejectReview: (id, data) => api.post(`/performance/reviews/${id}/reject/`, data),

  // Feedback
  listFeedback: () => api.get('/performance/feedback/'),
  createFeedback: (data) => api.post('/performance/feedback/', data),
}

export default performanceAPI
