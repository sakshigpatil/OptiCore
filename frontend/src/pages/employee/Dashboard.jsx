import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

const EmployeeDashboard = () => {
  const { user } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  
  const [dashboardData, setDashboardData] = useState({
    myTasks: { total: 0, pending: 0, completed: 0 },
    leaveBalance: 0,
    workingDaysThisMonth: 0,
    notifications: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchEmployeeDashboardData();
    }
  }, [user]);

  const fetchEmployeeDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch employee-specific data
      const [
        tasksResponse,
        leavesResponse,
        attendanceResponse,
        notificationsResponse
      ] = await Promise.all([
        api.get('/tasks/').catch(() => ({ data: [] })),
        api.get('/leave-requests/').catch(() => ({ data: [] })),
        api.get('/attendance/').catch(() => ({ data: [] })),
        api.get('/notifications/').catch(() => ({ data: [] }))
      ]);

      // Calculate employee metrics
      const allTasks = tasksResponse.data || [];
      const myTasks = allTasks.filter(task => task.assigned_to === user?.id || task.assignee === user?.id);
      const pendingTasks = myTasks.filter(task => task.status === 'PENDING' || task.status === 'IN_PROGRESS' || !task.status);
      const completedTasks = myTasks.filter(task => task.status === 'COMPLETED');
      
      const myLeaves = leavesResponse.data?.filter(leave => leave.employee === user?.id || leave.user === user?.id) || [];
      const approvedLeaves = myLeaves.filter(leave => leave.status === 'APPROVED');
      const totalLeaveDays = approvedLeaves.reduce((sum, leave) => {
        if (leave.start_date && leave.end_date) {
          const start = new Date(leave.start_date);
          const end = new Date(leave.end_date);
          const diffTime = Math.abs(end - start);
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
          return sum + diffDays;
        }
        return sum + (leave.days || 0);
      }, 0);
      
      // Calculate working days this month (rough estimate)
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const workingDaysThisMonth = Math.floor(daysInMonth * 0.71); // Rough estimate excluding weekends
      
      const myNotifications = notificationsResponse.data?.filter(notif => 
        notif.recipient === user?.id || notif.user === user?.id
      ) || [];
      const unreadNotifications = myNotifications.filter(notif => !notif.read || notif.is_read === false);

      setDashboardData({
        myTasks: {
          total: myTasks.length,
          pending: pendingTasks.length,
          completed: completedTasks.length
        },
        leaveBalance: Math.max(0, 25 - totalLeaveDays), // Assuming 25 days annual leave
        workingDaysThisMonth,
        notifications: unreadNotifications.length
      });
      
    } catch (err) {
      console.error('Error fetching employee dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'clock':
        navigate('/employee/attendance');
        break;
      case 'leave':
        navigate('/employee/leaves');
        break;
      case 'payslip':
        navigate('/employee/payslip');
        break;
      case 'profile':
        navigate('/employee/profile');
        break;
      default:
        break;
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Employee Dashboard</h1>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#3498db', marginBottom: '0.5rem' }}>My Tasks</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.myTasks.total}
              </div>
              <small style={{ color: '#7f8c8d' }}>
                {loading ? 'Loading...' : `${dashboardData.myTasks.pending} pending, ${dashboardData.myTasks.completed} completed`}
              </small>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#27ae60', marginBottom: '0.5rem' }}>Leave Balance</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.leaveBalance}
              </div>
              <small style={{ color: '#7f8c8d' }}>days remaining</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#f39c12', marginBottom: '0.5rem' }}>This Month</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.workingDaysThisMonth}
              </div>
              <small style={{ color: '#7f8c8d' }}>working days</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#e74c3c', marginBottom: '0.5rem' }}>Notifications</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.notifications}
              </div>
              <small style={{ color: '#7f8c8d' }}>unread messages</small>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header">Quick Actions</div>
          <div className="card-body">
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={() => handleQuickAction('clock')}>
                Clock In/Out
              </button>
              <button className="btn btn-secondary" onClick={() => handleQuickAction('leave')}>
                Request Leave
              </button>
              <button className="btn btn-success" onClick={() => handleQuickAction('payslip')}>
                View Payslip
              </button>
              <button className="btn btn-info" onClick={() => handleQuickAction('profile')}>
                Update Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;