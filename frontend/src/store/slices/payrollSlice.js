import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  payrollRecords: [],
  currentPayslip: null,
  isLoading: false,
  error: null,
}

const payrollSlice = createSlice({
  name: 'payroll',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { clearError } = payrollSlice.actions
export default payrollSlice.reducer