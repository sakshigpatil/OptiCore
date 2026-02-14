import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const PayrollDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    totalEmployees: 0,
    totalSalaryExpense: 0,
    pendingPayments: 0,
    completedPayrolls: 0,
    recentPayrolls: [],
    departmentWiseExpense: [],
    monthlyTrends: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, [selectedYear]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch payroll runs
      const payrollResponse = await api.get('/payroll-runs/');
      const payrollRuns = payrollResponse.results || payrollResponse.data || [];
      
      // Fetch salary structures
      const salaryResponse = await api.get('/salary-structures/');
      const salaryStructures = salaryResponse.results || salaryResponse.data || [];
      
      // Fetch payslips
      const payslipsResponse = await api.get('/payslips/');
      const payslips = payslipsResponse.results || payslipsResponse.data || [];
      
      // Calculate dashboard metrics
      const currentYearPayrolls = payrollRuns.filter(run => run.year === selectedYear);
      const totalSalaryExpense = payslips
        .filter(slip => slip.payroll_run && new Date(slip.generated_at).getFullYear() === selectedYear)
        .reduce((sum, slip) => sum + parseFloat(slip.net_salary || 0), 0);
      
      const pendingPayments = payslips.filter(slip => {
        const paymentStatus = slip.payment_status;
        return paymentStatus && paymentStatus.status === 'PENDING';
      }).length;
      
      // Group by department (simplified - using employee data)
      const departmentExpense = {};
      payslips.forEach(slip => {
        const dept = 'General'; // Simplified - would need employee department data
        if (!departmentExpense[dept]) departmentExpense[dept] = 0;
        departmentExpense[dept] += parseFloat(slip.net_salary || 0);
      });
      
      const departmentWiseExpense = Object.entries(departmentExpense).map(([dept, amount]) => ({
        department: dept,
        amount: amount
      }));
      
      // Monthly trends
      const monthlyTrends = [];
      for (let month = 1; month <= 12; month++) {
        const monthPayslips = payslips.filter(slip => {
          const slipDate = new Date(slip.generated_at);
          return slipDate.getFullYear() === selectedYear && slipDate.getMonth() + 1 === month;
        });
        const monthTotal = monthPayslips.reduce((sum, slip) => sum + parseFloat(slip.net_salary || 0), 0);
        monthlyTrends.push({
          month: new Date(selectedYear, month - 1).toLocaleString('default', { month: 'short' }),
          amount: monthTotal,
          employeeCount: monthPayslips.length
        });
      }
      
      setDashboardData({
        totalEmployees: salaryStructures.length,
        totalSalaryExpense: totalSalaryExpense,
        pendingPayments: pendingPayments,
        completedPayrolls: currentYearPayrolls.filter(run => run.processed).length,
        recentPayrolls: payrollRuns.slice(0, 5),
        departmentWiseExpense: departmentWiseExpense,
        monthlyTrends: monthlyTrends
      });
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load payroll data. Please try again.');
      // Set default data to prevent undefined errors in UI
      setDashboardData({
        totalEmployees: 0,
        totalSalaryExpense: 0,
        pendingPayments: 0,
        completedPayrolls: 0,
        recentPayrolls: [],
        departmentWiseExpense: [],
        monthlyTrends: []
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatMonth = (month, year) => {
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading...</span>
        </div>
        <p style={{ marginTop: '1rem' }}>Loading dashboard data...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Payroll Dashboard</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <label>Year:</label>
          <select 
            value={selectedYear} 
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="form-control"
            style={{ width: 'auto' }}
          >
            {[2023, 2024, 2025, 2026].map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>
      
      {error && (
        <div className="alert alert-warning" style={{ margin: '1rem 0' }}>
          <strong>⚠️ {error}</strong>
          <button 
            className="btn btn-sm btn-primary" 
            style={{ marginLeft: '1rem' }}
            onClick={() => fetchDashboardData()}
          >
            Retry
          </button>
        </div>
      )}
      
      <div className="page-content">
        {/* Key Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#3498db', margin: 0 }}> Total Employees</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {dashboardData.totalEmployees}
              </div>
              <small style={{ color: '#666' }}>Active salary structures</small>
            </div>
          </div>
          
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#27ae60', margin: 0 }}> Total Expense</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {formatCurrency(dashboardData.totalSalaryExpense)}
              </div>
              <small style={{ color: '#666' }}>Year {selectedYear}</small>
            </div>
          </div>
          
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#f39c12', margin: 0 }}> Pending Payments</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {dashboardData.pendingPayments}
              </div>
              <small style={{ color: '#666' }}>Awaiting payment</small>
            </div>
          </div>
          
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#9b59b6', margin: 0 }}> Completed</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
                {dashboardData.completedPayrolls}
              </div>
              <small style={{ color: '#666' }}>Payroll runs</small>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          {/* Monthly Trends Chart */}
          <div className="card">
            <div className="card-header">
              <h5 style={{ margin: 0 }}> Monthly Salary Trends - {selectedYear}</h5>
            </div>
            <div className="card-body">
              <div style={{ overflowX: 'auto' }}>
                <table className="table table-sm">
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Amount</th>
                      <th>Employees</th>
                      <th>Avg Salary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardData.monthlyTrends.map((trend, index) => (
                      <tr key={index}>
                        <td>{trend.month}</td>
                        <td style={{ color: '#27ae60', fontWeight: 'bold' }}>
                          {formatCurrency(trend.amount)}
                        </td>
                        <td>{trend.employeeCount}</td>
                        <td>
                          {trend.employeeCount > 0 
                            ? formatCurrency(trend.amount / trend.employeeCount)
                            : '$0'
                          }
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Simple bar chart visualization */}
              <div style={{ marginTop: '1rem' }}>
                <h6>Visual Trend:</h6>
                <div style={{ display: 'flex', alignItems: 'end', gap: '0.25rem', height: '100px' }}>
                  {dashboardData.monthlyTrends.map((trend, index) => {
                    const maxAmount = Math.max(...dashboardData.monthlyTrends.map(t => t.amount));
                    const height = maxAmount > 0 ? (trend.amount / maxAmount) * 80 : 0;
                    return (
                      <div 
                        key={index}
                        style={{
                          backgroundColor: '#3498db',
                          height: `${height}px`,
                          minHeight: trend.amount > 0 ? '5px' : '0px',
                          width: '100%',
                          borderRadius: '2px 2px 0 0',
                          title: `${trend.month}: ${formatCurrency(trend.amount)}`
                        }}
                      />
                    );
                  })}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  {dashboardData.monthlyTrends.map((trend, index) => (
                    <span key={index}>{trend.month}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Payrolls & Department Breakdown */}
          <div>
            {/* Recent Payrolls */}
            <div className="card" style={{ marginBottom: '1rem' }}>
              <div className="card-header">
                <h5 style={{ margin: 0 }}> Recent Payrolls</h5>
              </div>
              <div className="card-body">
                {dashboardData.recentPayrolls.length === 0 ? (
                  <p style={{ textAlign: 'center', color: '#666' }}>No payroll runs found</p>
                ) : (
                  <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {dashboardData.recentPayrolls.map((run) => (
                      <div 
                        key={run.id} 
                        style={{ 
                          padding: '0.75rem', 
                          borderBottom: '1px solid #eee',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <div>
                          <strong>{formatMonth(run.month, run.year)}</strong>
                          <br />
                          <small style={{ color: '#666' }}>
                            {new Date(run.created_at).toLocaleDateString()}
                          </small>
                        </div>
                        <div>
                          <span 
                            style={{ 
                              color: run.processed ? '#27ae60' : '#f39c12',
                              fontWeight: 'bold',
                              fontSize: '0.8rem'
                            }}
                          >
                            {run.processed ? ' Done' : ' Pending'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Department Breakdown */}
            <div className="card">
              <div className="card-header">
                <h5 style={{ margin: 0 }}>🏢 Department Expense</h5>
              </div>
              <div className="card-body">
                {dashboardData.departmentWiseExpense.length === 0 ? (
                  <p style={{ textAlign: 'center', color: '#666' }}>No department data</p>
                ) : (
                  dashboardData.departmentWiseExpense.map((dept, index) => (
                    <div 
                      key={index}
                      style={{ 
                        padding: '0.5rem 0',
                        borderBottom: index < dashboardData.departmentWiseExpense.length - 1 ? '1px solid #eee' : 'none'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>{dept.department}</span>
                        <strong style={{ color: '#27ae60' }}>
                          {formatCurrency(dept.amount)}
                        </strong>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div className="card-header">
            <h5 style={{ margin: 0 }}>⚡ Quick Actions</h5>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <button 
                className="btn btn-primary"
                onClick={() => window.location.href = '/hr/payroll'}
                style={{ padding: '1rem' }}
              >
                 Manage Payroll
              </button>
              <button 
                className="btn btn-success"
                onClick={() => window.location.href = '/hr/employees'}
                style={{ padding: '1rem' }}
              >
                 Manage Employees
              </button>
              <button 
                className="btn btn-info"
                onClick={() => window.location.href = '/hr/attendance'}
                style={{ padding: '1rem' }}
              >
                 View Attendance
              </button>
              <button 
                className="btn btn-warning"
                onClick={() => {
                  const currentMonth = new Date().getMonth() + 1;
                  const currentYear = new Date().getFullYear();
                  // This would ideally trigger payroll creation
                  alert(`Create payroll for ${currentMonth}/${currentYear}?`);
                }}
                style={{ padding: '1rem' }}
              >
                 Run Payroll
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PayrollDashboard;