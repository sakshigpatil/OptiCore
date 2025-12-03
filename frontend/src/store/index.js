import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import employeeSlice from './slices/employeeSlice'
import departmentSlice from './slices/departmentSlice'
import projectSlice from './slices/projectSlice'
import taskSlice from './slices/taskSlice'
import attendanceSlice from './slices/attendanceSlice'
import leaveSlice from './slices/leaveSlice'
import payrollSlice from './slices/payrollSlice'
import notificationSlice from './slices/notificationSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    employee: employeeSlice,
    department: departmentSlice,
    project: projectSlice,
    task: taskSlice,
    attendance: attendanceSlice,
    leave: leaveSlice,
    payroll: payrollSlice,
    notification: notificationSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
})