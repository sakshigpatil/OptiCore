import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  departments: [],
  isLoading: false,
  error: null,
}

const departmentSlice = createSlice({
  name: 'department',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { clearError } = departmentSlice.actions
export default departmentSlice.reducer