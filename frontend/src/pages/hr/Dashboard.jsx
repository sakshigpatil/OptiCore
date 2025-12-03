import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const HRDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    totalEmployees: 0,
    activeProjects: 0,
    pendingLeaves: 0,
    monthlyPayroll: 0,
    pendingApprovals: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all dashboard data in parallel
      const [
        employeesResponse,
        projectsResponse,
        leavesResponse,
        payrollResponse,
        approvalsResponse
      ] = await Promise.all([
        api.get('/employees/').catch(() => ({ data: [] })),
        api.get('/projects/').catch(() => ({ data: [] })),
        api.get('/leave-requests/').catch(() => ({ data: [] })),
        api.get('/payroll/').catch(() => ({ data: [] })),
        api.get('/users/').catch(() => ({ data: [] }))
      ]);

      // Calculate metrics from real data
      const totalEmployees = employeesResponse.data?.length || 0;
      const activeProjects = projectsResponse.data?.filter(p => p.status === 'ACTIVE' || !p.status)?.length || projectsResponse.data?.length || 0;
      const pendingLeaves = leavesResponse.data?.filter(l => l.status === 'PENDING')?.length || 0;
      const monthlyPayroll = payrollResponse.data?.reduce((sum, record) => sum + (record.net_salary || 0), 0) || 0;
      const pendingApprovals = Array.isArray(approvalsResponse.data) 
        ? approvalsResponse.data.filter(u => u.approval_status === 'PENDING').length 
        : 0;

      setDashboardData({
        totalEmployees,
        activeProjects,
        pendingLeaves,
        monthlyPayroll,
        pendingApprovals
      });
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        config: err.config?.url
      });
      // Keep default values on error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">HR Dashboard</h1>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#3498db', marginBottom: '0.5rem' }}>Total Employees</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.totalEmployees}
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#27ae60', marginBottom: '0.5rem' }}>Active Projects</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.activeProjects}
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#f39c12', marginBottom: '0.5rem' }}>Pending Leaves</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.pendingLeaves}
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#e74c3c', marginBottom: '0.5rem' }}>This Month Payroll</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : `$${dashboardData.monthlyPayroll.toLocaleString()}`}
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body">
              <h3 style={{ color: '#9b59b6', marginBottom: '0.5rem' }}>Pending Approvals</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {loading ? '...' : dashboardData.pendingApprovals}
              </div>
              {!loading && dashboardData.pendingApprovals > 0 && (
                <Link 
                  to="/hr/employee-approvals" 
                  style={{ 
                    color: '#9b59b6', 
                    textDecoration: 'none', 
                    fontSize: '0.875rem',
                    fontWeight: 'bold'
                  }}
                >
                  View Requests →
                </Link>
              )}
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header">Recent Activities</div>
          <div className="card-body">
            <p>Welcome to the HR Management Dashboard. Here you can manage employees, track attendance, process leaves, and handle payroll.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HRDashboard;