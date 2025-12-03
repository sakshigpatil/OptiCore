import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  tasks: [],
  myTasks: [],
  currentTask: null,
  isLoading: false,
  error: null,
}

const taskSlice = createSlice({
  name: 'task',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { clearError } = taskSlice.actions
export default taskSlice.reducer