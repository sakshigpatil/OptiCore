import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { Toaster } from 'react-hot-toast'
import { getCurrentUser } from './store/slices/authSlice'

// Layout Components
import Layout from './components/layout/Layout'
import AuthLayout from './components/layout/AuthLayout'

// Authentication Pages
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'

// HR Pages
import HRDashboard from './pages/hr/Dashboard'
import Employees from './pages/hr/Employees'

// Manager Pages
import ManagerDashboard from './pages/manager/Dashboard'
import Departments from './pages/hr/Departments'
import Leaves from './pages/hr/Leaves'
import Attendance from './pages/hr/Attendance'
import Payroll from './pages/hr/Payroll'
import EmployeeApprovals from './pages/hr/EmployeeApprovals'
import SkillAnalysis from './pages/hr/SkillAnalysis'
import ScheduledReports from './pages/hr/ScheduledReports'
import CustomReports from './pages/hr/CustomReports'

// Employee Pages
import EmployeeDashboard from './pages/employee/Dashboard'
import Profile from './pages/employee/Profile'
import Tasks from './pages/employee/Tasks'
import MyAttendance from './pages/employee/Attendance'
import MyLeaves from './pages/employee/Leaves'
import Payslip from './pages/employee/Payslip'

// Shared Pages
import NotFound from './pages/shared/NotFound'
import Unauthorized from './pages/shared/Unauthorized'

// Route Guards
import ProtectedRoute from './components/auth/ProtectedRoute'
import RoleBasedRoute from './components/auth/RoleBasedRoute'

function App() {
  const dispatch = useDispatch()
  const { token, isAuthenticated, user, isLoading } = useSelector((state) => state.auth)

  useEffect(() => {
    // Clear invalid tokens on app startup
    const validateAndCleanTokens = () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken && storedToken !== 'null' && storedToken !== 'undefined') {
        try {
          // Basic JWT validation - check if it has 3 parts
          const parts = storedToken.split('.')
          if (parts.length !== 3) {
            console.warn('Invalid token format detected, clearing localStorage')
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            window.location.reload()
            return
          }
        } catch (e) {
          console.warn('Error validating token, clearing localStorage')
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          window.location.reload()
          return
        }
      }
    }

    validateAndCleanTokens()

    if (token && !user) {
      dispatch(getCurrentUser())
    }
  }, [dispatch, token, user])

  return (
    <div className="App">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            !isAuthenticated ? (
              <Login />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route
          path="/register"
          element={
            !isAuthenticated ? (
              <AuthLayout>
                <Register />
              </AuthLayout>
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard Route - Redirect based on role */}
          <Route
            index
            element={
              isLoading ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}>
                  <div className="spinner-border" role="status">
                    <span className="sr-only">Loading...</span>
                  </div>
                  <p style={{ marginTop: '1rem' }}>Loading user data...</p>
                </div>
              ) : user?.role === 'ADMIN_HR' ? (
                <Navigate to="/hr/dashboard" replace />
              ) : user?.role === 'MANAGER' ? (
                <Navigate to="/manager/dashboard" replace />
              ) : user?.role === 'EMPLOYEE' ? (
                <Navigate to="/employee/dashboard" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          {/* HR Routes */}
          <Route
            path="hr/*"
            element={
              <RoleBasedRoute allowedRoles={['ADMIN_HR']}>
                <Routes>
                  <Route path="dashboard" element={<HRDashboard />} />
                  <Route path="employees" element={<Employees />} />
                  <Route path="skill-analysis" element={<SkillAnalysis />} />
                  <Route path="departments" element={<Departments />} />
                  <Route path="leaves" element={<Leaves />} />
                  <Route path="attendance" element={<Attendance />} />
                  <Route path="payroll" element={<Payroll />} />
                  <Route path="employee-approvals" element={<EmployeeApprovals />} />
                  <Route path="scheduled-reports" element={<ScheduledReports />} />
                  <Route path="custom-reports" element={<CustomReports />} />
                </Routes>
              </RoleBasedRoute>
            }
          />

          {/* Manager Routes */}
          <Route
            path="manager/*"
            element={
              <RoleBasedRoute allowedRoles={['MANAGER']}>
                <Routes>
                  <Route path="dashboard" element={<ManagerDashboard />} />
                  <Route path="employees" element={<Employees />} />
                  <Route path="leaves" element={<Leaves />} />
                  <Route path="attendance" element={<Attendance />} />
                  <Route path="employee-approvals" element={<EmployeeApprovals />} />
                </Routes>
              </RoleBasedRoute>
            }
          />

          {/* Employee Routes */}
          <Route
            path="employee/*"
            element={
              // Redirect HR admins and managers to their own dashboards
              user?.role === 'ADMIN_HR' ? (
                <Navigate to="/hr/dashboard" replace />
              ) : user?.role === 'MANAGER' ? (
                <Navigate to="/manager/dashboard" replace />
              ) : (
                <RoleBasedRoute allowedRoles={['EMPLOYEE']}>
                  <Routes>
                    <Route path="dashboard" element={<EmployeeDashboard />} />
                    <Route path="profile" element={<Profile />} />
                    <Route path="tasks" element={<Tasks />} />
                    <Route path="attendance" element={<MyAttendance />} />
                    <Route path="leaves" element={<MyLeaves />} />
                    <Route path="payslip" element={<Payslip />} />
                  </Routes>
                </RoleBasedRoute>
              )
            }
          />
        </Route>

        {/* Error Routes */}
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

export default App