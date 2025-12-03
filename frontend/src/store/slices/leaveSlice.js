import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  leaveRequests: [],
  leaveBalance: {},
  leaveTypes: [],
  isLoading: false,
  error: null,
}

const leaveSlice = createSlice({
  name: 'leave',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { clearError } = leaveSlice.actions
export default leaveSlice.reducer