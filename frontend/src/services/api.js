import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Enhanced logging for debugging network issues
    console.log('🚀 API Request:', {
      url: config.url,
      method: config.method,
      baseURL: config.baseURL,
      headers: config.headers,
      data: config.data,
      timeout: config.timeout
    })
    
    const token = localStorage.getItem('token')
    if (token && token !== 'null' && token !== 'undefined') {
      try {
        // Basic token validation - check if it looks like a JWT
        const parts = token.split('.')
        if (parts.length === 3) {
          config.headers.Authorization = `Bearer ${token}`
          console.log('✅ Token added to request')
        } else {
          // Invalid token format, remove it
          console.warn('⚠️ Invalid token format, removing from localStorage')
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
        }
      } catch (e) {
        console.warn('⚠️ Error processing token, removing from localStorage', e)
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
      }
    } else {
      console.log('ℹ️ No token found in localStorage')
    }
    return config
  },
  (error) => {
    console.error('❌ Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config?.url,
      data: response.data
    })
    return response.data
  },
  async (error) => {
    console.error('❌ API Error Details:', {
      message: error.message,
      code: error.code,
      response: error.response,
      request: error.request,
      config: error.config
    })
    
    // Log network-specific errors
    if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
      console.error('🔴 NETWORK ERROR DETECTED:', {
        baseURL: error.config?.baseURL,
        url: error.config?.url,
        method: error.config?.method,
        timeout: error.config?.timeout,
        headers: error.config?.headers
      })
    }
    
    const originalRequest = error.config

    // Handle 401 errors or token validation errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Check if it's a token validation error
      const errorDetail = error.response?.data?.detail || ''
      if (errorDetail.includes('token not valid') || errorDetail.includes('Invalid token')) {
        console.warn('Invalid token detected, clearing localStorage')
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        // Only redirect if not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }

      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (refreshToken) {
          const response = await axios.post(
            `${api.defaults.baseURL}/auth/token/refresh/`,
            { refresh: refreshToken }
          )
          
          const { access } = response.data
          localStorage.setItem('token', access)
          
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }
    }

    // Don't show toast for login/auth errors in components
    // Let the components handle auth-related error messages
    if (error.response?.status !== 401 && !originalRequest.url?.includes('/auth/')) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          error.message ||
                          'An error occurred'
      toast.error(errorMessage)
    }

    return Promise.reject(error)
  }
)

export default api