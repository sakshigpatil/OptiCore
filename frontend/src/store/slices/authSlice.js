import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import authService from '../../services/auth'

// Initial state
const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,
}

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authService.login(credentials)
      const token = response.access || response.token
      const refreshToken = response.refresh || response.refreshToken
      
      if (token) localStorage.setItem('token', token)
      if (refreshToken) localStorage.setItem('refreshToken', refreshToken)
      
      return response
    } catch (error) {
      console.error('Login error:', error)
      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.message ||
                          error.response?.data?.non_field_errors?.[0] ||
                          error.message ||
                          'Login failed'
      return rejectWithValue(errorMessage)
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authService.register(userData)
      const token = response.access || response.token
      const refreshToken = response.refresh || response.refreshToken
      
      if (token) localStorage.setItem('token', token)
      if (refreshToken) localStorage.setItem('refreshToken', refreshToken)
      
      return response
    } catch (error) {
      console.error('Registration error:', error)
      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.message ||
                          error.response?.data?.non_field_errors?.[0] ||
                          error.message ||
                          'Registration failed'
      return rejectWithValue(errorMessage)
    }
  }
)

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      
      // Always clear local storage first
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      
      // Try to call logout API, but don't fail if it doesn't work
      if (refreshToken && refreshToken !== 'null' && refreshToken !== 'undefined') {
        try {
          await authService.logout({ refresh: refreshToken })
        } catch (apiError) {
          console.warn('Logout API call failed, but continuing with logout:', apiError)
        }
      }
      
      return true
    } catch (error) {
      // Ensure cleanup even if everything fails
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      return true // Don't reject, always allow logout
    }
  }
)

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authService.getCurrentUser()
      return response
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to get user')
    }
  }
)

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authService.updateProfile(userData)
      return response
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Update failed')
    }
  }
)

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async (passwordData, { rejectWithValue }) => {
    try {
      await authService.changePassword(passwordData)
      return true
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Password change failed')
    }
  }
)

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setCredentials: (state, action) => {
      state.user = action.payload.user
      state.token = action.payload.token
      state.isAuthenticated = true
    },
    clearCredentials: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      state.error = null
      // Clear localStorage as well
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.user = action.payload.user
        state.token = action.payload.access || action.payload.token
        state.error = null
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = action.payload
      })
      // Register
      .addCase(register.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.user = action.payload.user
        state.token = action.payload.access || action.payload.token
        state.error = null
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = null
      })
      .addCase(logout.rejected, (state) => {
        // Even if logout API fails, clear the auth state
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = null
      })
      // Get current user
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.user = action.payload
        state.error = null
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = action.payload
      })
      // Update profile
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.user = action.payload
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.error = action.payload
      })
      // Change password
      .addCase(changePassword.rejected, (state, action) => {
        state.error = action.payload
      })
  },
})

export const { clearError, setCredentials, clearCredentials } = authSlice.actions
export default authSlice.reducer