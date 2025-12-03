import api from './api'

const authService = {
  // Login
  login: async (credentials) => {
    const response = await api.post('/auth/login/', credentials)
    return response
  },

  // Register
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData)
    return response
  },

  // Logout
  logout: async (data) => {
    const response = await api.post('/auth/logout/', data)
    return response
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/auth/me/')
    return response
  },

  // Update profile
  updateProfile: async (userData) => {
    const response = await api.put('/auth/update_profile/', userData)
    return response
  },

  // Change password
  changePassword: async (passwordData) => {
    const response = await api.post('/auth/change_password/', passwordData)
    return response
  },

  // Refresh token
  refreshToken: async (refreshToken) => {
    const response = await api.post('/auth/token/refresh/', {
      refresh: refreshToken
    })
    return response
  },

  // Password reset request
  requestPasswordReset: async (email) => {
    const response = await api.post('/auth/password/reset/', { email })
    return response
  },

  // Password reset confirm
  confirmPasswordReset: async (data) => {
    const response = await api.post('/auth/password/reset/confirm/', data)
    return response
  },
}

export default authService