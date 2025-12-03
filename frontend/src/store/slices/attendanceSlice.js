import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  attendanceRecords: [],
  todayAttendance: null,
  isLoading: false,
  error: null,
}

const attendanceSlice = createSlice({
  name: 'attendance',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { clearError } = attendanceSlice.actions
export default attendanceSlice.reducer