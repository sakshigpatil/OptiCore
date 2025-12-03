import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  projects: [],
  currentProject: null,
  isLoading: false,
  error: null,
}

const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { clearError } = projectSlice.actions
export default projectSlice.reducer