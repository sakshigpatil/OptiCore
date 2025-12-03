import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

// Initial state
const initialState = {
  employees: [],
  currentEmployee: null,
  isLoading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
  },
}

// Async thunks would be implemented here
export const fetchEmployees = createAsyncThunk(
  'employee/fetchEmployees',
  async (params = {}) => {
    // API call would be implemented
    return { results: [], count: 0 }
  }
)

// Employee slice
const employeeSlice = createSlice({
  name: 'employee',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setCurrentEmployee: (state, action) => {
      state.currentEmployee = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchEmployees.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchEmployees.fulfilled, (state, action) => {
        state.isLoading = false
        state.employees = action.payload.results
        state.pagination = {
          count: action.payload.count,
          next: action.payload.next,
          previous: action.payload.previous,
        }
      })
      .addCase(fetchEmployees.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload
      })
  },
})

export const { clearError, setCurrentEmployee } = employeeSlice.actions
export default employeeSlice.reducer