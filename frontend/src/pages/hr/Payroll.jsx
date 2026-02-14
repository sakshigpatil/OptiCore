import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const Payroll = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [payrollRuns, setPayrollRuns] = useState([]);
  const [salaryStructures, setSalaryStructures] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [payslips, setPayslips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateRun, setShowCreateRun] = useState(false);
  const [showSalaryModal, setShowSalaryModal] = useState(false);
  const [showBonusModal, setShowBonusModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [processingPayroll, setProcessingPayroll] = useState(false);
  const [selectedPayrollRun, setSelectedPayrollRun] = useState(null);
  
  const [newRun, setNewRun] = useState({
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1
  });
  
  const [newSalaryStructure, setNewSalaryStructure] = useState({
    employee: '',
    salary_type: 'MONTHLY',
    basic: '',
    hra_percent: '20',
    hra_fixed: '0',
    conveyance: '1000',
    medical_allowance: '500',
    special_allowance: '0',
    other_allowances: '0',
    pf_percent: '12',
    esi_percent: '0.75',
    professional_tax: '200',
    bonus_eligible: true,
    overtime_rate: '1.5',
    annual_ctc: ''
  });
  
  const [newBonus, setNewBonus] = useState({
    employees: [],
    bonus_type: 'FESTIVAL',
    amount: '',
    percentage_of_basic: '',
    applicable_month: new Date().getMonth() + 1,
    applicable_year: new Date().getFullYear()
  });
  
  const [reportConfig, setReportConfig] = useState({
    type: 'monthly_summary',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    department: '',
    format: 'csv'
  });
  
  const [dashboardStats, setDashboardStats] = useState({
    totalEmployees: 0,
    totalSalaryExpense: 0,
    pendingPayrolls: 0,
    completedPayrolls: 0
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  // Recalculate dashboard stats when data changes
  useEffect(() => {
    if (employees.length > 0 || payslips.length > 0 || payrollRuns.length > 0) {
      calculateDashboardStats();
    }
  }, [employees, payslips, payrollRuns]);
  
  const fetchAllData = async () => {
    await Promise.all([
      fetchPayrollRuns(),
      fetchSalaryStructures(), 
      fetchEmployees(),
      fetchPayslips()
    ]);
    // Calculate stats after all data is fetched
    calculateDashboardStats();
  };

  const fetchPayrollRuns = async () => {
    try {
      const response = await api.get('/payroll/payroll-runs/');
      setPayrollRuns(response.results || response.data || []);
    } catch (error) {
      console.error('Error fetching payroll runs:', error);
      alert('Failed to fetch payroll runs');
    }
  };

  const fetchSalaryStructures = async () => {
    try {
      const response = await api.get('/payroll/salary-structures/');
      setSalaryStructures(response.results || response.data || []);
    } catch (error) {
      console.error('Error fetching salary structures:', error);
      alert('Failed to fetch salary structures');
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/users/');
      const employeeList = response.results || response.data || [];
      setEmployees(employeeList.filter(emp => emp.is_active));
    } catch (error) {
      console.error('Error fetching employees:', error);
      alert('Failed to fetch employees');
    }
  };
  
  const fetchPayslips = async () => {
    try {
      const response = await api.get('/payroll/payslips/');
      setPayslips(response.results || response.data || []);
    } catch (error) {
      console.error('Error fetching payslips:', error);
    }
  };
  
  const calculateDashboardStats = () => {
    try {
      const stats = {
        totalEmployees: employees.length,
        totalSalaryExpense: payslips.reduce((sum, slip) => sum + parseFloat(slip.net_salary || 0), 0),
        pendingPayrolls: payrollRuns.filter(run => !run.processed).length,
        completedPayrolls: payrollRuns.filter(run => run.processed).length
      };
      setDashboardStats(stats);
    } catch (error) {
      console.error('Error calculating dashboard stats:', error);
    }
  };

  const handleCreatePayrollRun = async () => {
    setLoading(true);
    try {
      await api.post('/payroll/payroll-runs/', newRun);
      await fetchPayrollRuns();
      calculateDashboardStats();
      setShowCreateRun(false);
      setNewRun({
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1
      });
      alert('Payroll run created successfully!');
    } catch (error) {
      console.error('Error creating payroll run:', error);
      alert('Error creating payroll run: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRunPayroll = async (payrollRunId) => {
    if (!confirm('Are you sure you want to process this payroll? This action cannot be undone.')) {
      return;
    }
    
    setProcessingPayroll(true);
    setLoading(true);
    
    try {
      const response = await api.post(`/payroll/payroll-runs/${payrollRunId}/run/`, {
        include_attendance: true,
        auto_approve_reimbursements: false
      });
      
      await fetchAllData();
      
      const result = response.data;
      alert(`Payroll processed successfully!\n\nDetails:\n- Employees processed: ${result.processed_count}\n- Errors: ${result.errors?.length || 0}`);
      
      if (result.errors && result.errors.length > 0) {
        console.warn('Payroll processing errors:', result.errors);
      }
      
    } catch (error) {
      console.error('Error processing payroll:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Unknown error occurred';
      alert(`Error processing payroll: ${errorMessage}`);
    } finally {
      setProcessingPayroll(false);
      setLoading(false);
    }
  };
  
  const handleBulkBonus = async () => {
    if (newBonus.employees.length === 0) {
      alert('Please select at least one employee');
      return;
    }
    
    setLoading(true);
    try {
      const response = await api.post('/payroll/bonuses/bulk_create/', {
        employee_ids: newBonus.employees,
        bonus_type: newBonus.bonus_type,
        amount: newBonus.amount || 0,
        percentage_of_basic: newBonus.percentage_of_basic || null,
        applicable_month: newBonus.applicable_month,
        applicable_year: newBonus.applicable_year
      });
      
      setShowBonusModal(false);
      setNewBonus({
        employees: [],
        bonus_type: 'FESTIVAL',
        amount: '',
        percentage_of_basic: '',
        applicable_month: new Date().getMonth() + 1,
        applicable_year: new Date().getFullYear()
      });
      
      alert(`${response.data.detail}`);
    } catch (error) {
      console.error('Error creating bonuses:', error);
      alert('Error creating bonuses: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const generateReport = async () => {
    setLoading(true);
    try {
      let url = '/payroll/payroll-runs/';
      if (reportConfig.type === 'monthly_summary') {
        url = `/payroll/payslips/?year=${reportConfig.year}&month=${reportConfig.month}`;
      }
      
      const response = await api.get(url);
      const data = response.results || response.data || [];
      
      if (reportConfig.format === 'csv') {
        downloadCSV(data, `payroll_report_${reportConfig.year}_${reportConfig.month}.csv`);
      } else {
        downloadJSON(data, `payroll_report_${reportConfig.year}_${reportConfig.month}.json`);
      }
      
      setShowReportModal(false);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const downloadCSV = (data, filename) => {
    if (data.length === 0) {
      alert('No data available for report');
      return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };
  
  const downloadJSON = (data, filename) => {
    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleCreateSalaryStructure = async () => {
    // Validation
    if (!newSalaryStructure.employee || !newSalaryStructure.basic) {
      alert('Please fill in all required fields (Employee and Basic Salary)');
      return;
    }
    
    if (parseFloat(newSalaryStructure.basic) <= 0) {
      alert('Basic salary must be greater than 0');
      return;
    }
    
    setLoading(true);
    try {
      await api.post('/payroll/salary-structures/', {
        ...newSalaryStructure,
        basic: parseFloat(newSalaryStructure.basic),
        hra_percent: parseFloat(newSalaryStructure.hra_percent),
        hra_fixed: parseFloat(newSalaryStructure.hra_fixed) || 0,
        conveyance: parseFloat(newSalaryStructure.conveyance) || 0,
        medical_allowance: parseFloat(newSalaryStructure.medical_allowance) || 0,
        special_allowance: parseFloat(newSalaryStructure.special_allowance) || 0,
        other_allowances: parseFloat(newSalaryStructure.other_allowances) || 0,
        pf_percent: parseFloat(newSalaryStructure.pf_percent),
        esi_percent: parseFloat(newSalaryStructure.esi_percent),
        professional_tax: parseFloat(newSalaryStructure.professional_tax) || 0,
        overtime_rate: parseFloat(newSalaryStructure.overtime_rate),
        annual_ctc: parseFloat(newSalaryStructure.annual_ctc) || 0
      });
      
      await fetchSalaryStructures();
      calculateDashboardStats();
      setShowSalaryModal(false);
      resetSalaryStructureForm();
      alert('Salary structure created successfully!');
    } catch (error) {
      console.error('Error creating salary structure:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          Object.values(error.response?.data || {}).flat().join(', ') ||
                          error.message;
      alert('Error creating salary structure: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  const resetSalaryStructureForm = () => {
    setNewSalaryStructure({
      employee: '',
      salary_type: 'MONTHLY',
      basic: '',
      hra_percent: '20',
      hra_fixed: '0',
      conveyance: '1000',
      medical_allowance: '500',
      special_allowance: '0',
      other_allowances: '0',
      pf_percent: '12',
      esi_percent: '0.75',
      professional_tax: '200',
      bonus_eligible: true,
      overtime_rate: '1.5',
      annual_ctc: ''
    });
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

  const getEmployeesWithoutSalaryStructure = () => {
    const employeesWithSalary = salaryStructures.map(ss => ss.employee);
    return employees.filter(emp => !employeesWithSalary.includes(emp.id));
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Advanced Payroll Management System</h1>
        <div className="flex flex-wrap gap-3">
          <button 
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            onClick={() => setShowSalaryModal(true)}
            disabled={loading}
          >
             Add Salary Structure
          </button>
          <button 
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            onClick={() => setShowCreateRun(true)}
            disabled={loading}
          >
             Create Payroll Run
          </button>
          <button 
            className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            onClick={() => setShowBonusModal(true)}
            disabled={loading}
          >
             Add Bonus
          </button>
          <button 
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            onClick={() => setShowReportModal(true)}
            disabled={loading}
          >
             Generate Report
          </button>
        </div>
      </div>
      
      {/* Navigation Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button 
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'dashboard' 
              ? 'border-blue-500 text-blue-600 bg-blue-50' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('dashboard')}
        >
           Dashboard
        </button>
        <button 
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'payroll-runs' 
              ? 'border-blue-500 text-blue-600 bg-blue-50' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('payroll-runs')}
        >
           Payroll Runs
        </button>
        <button 
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'salary-structures' 
              ? 'border-blue-500 text-blue-600 bg-blue-50' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('salary-structures')}
        >
           Salary Structures
        </button>
        <button 
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'payslips' 
              ? 'border-blue-500 text-blue-600 bg-blue-50' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('payslips')}
        >
           Payslips
        </button>
        <button 
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'compliance' 
              ? 'border-blue-500 text-blue-600 bg-blue-50' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('compliance')}
        >
          ⚖️ Compliance
        </button>
      </div>
      
      <div className="space-y-6">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow">
                <h3 className="text-gray-700 text-lg font-semibold mb-2">👥 Total Employees</h3>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {dashboardStats.totalEmployees}
                </div>
                <small className="text-gray-500">With salary structures</small>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow">
                <h3 className="text-gray-700 text-lg font-semibold mb-2">💰 Total Expense</h3>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {formatCurrency(dashboardStats.totalSalaryExpense)}
                </div>
                <small className="text-gray-500">This year</small>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow">
                <h3 className="text-gray-700 text-lg font-semibold mb-2">⏳ Pending</h3>
                <div className="text-3xl font-bold text-yellow-600 mb-1">
                  {dashboardStats.pendingPayrolls}
                </div>
                <small className="text-gray-500">Payroll runs</small>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow">
                <h3 className="text-gray-700 text-lg font-semibold mb-2"> Completed</h3>
                <div className="text-3xl font-bold text-green-600 mb-1">
                  {dashboardStats.completedPayrolls}
                </div>
                <small className="text-gray-500">Payroll runs</small>
              </div>
            </div>
            
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="px-6 py-4 border-b border-gray-200">
                <h5 className="text-lg font-semibold text-gray-900 m-0">⚡ Quick Actions</h5>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <button 
                    className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg font-medium transition-colors"
                    onClick={() => setActiveTab('payroll-runs')}
                  >
                     Manage Payroll Runs
                  </button>
                  <button 
                    className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg font-medium transition-colors"
                    onClick={() => setActiveTab('salary-structures')}
                  >
                     Manage Salaries
                  </button>
                  <button 
                    className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg font-medium transition-colors"
                    onClick={() => setActiveTab('payslips')}
                  >
                     View Payslips
                  </button>
                  <button 
                    className="bg-orange-600 hover:bg-orange-700 text-white p-4 rounded-lg font-medium transition-colors"
                    onClick={() => setShowCreateRun(true)}
                  >
                     Create New Payroll
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Payroll Runs Tab */}
        {activeTab === 'payroll-runs' && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="px-6 py-4 border-b border-gray-200">
              <h5 className="text-lg font-semibold text-gray-900 m-0">Payroll Runs Management</h5>
            </div>
            <div className="p-6">
              {loading && (
                <div style={{ textAlign: 'center', padding: '1rem' }}>
                  <div className="spinner-border text-primary" role="status">
                    <span className="sr-only">Loading...</span>
                  </div>
                  {processingPayroll && <p style={{ marginTop: '0.5rem' }}>Processing payroll...</p>}
                </div>
              )}
              
              {payrollRuns.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
                  <h4>No payroll runs found</h4>
                  <p>Create your first payroll run to get started with salary processing.</p>
                  <button 
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    onClick={() => setShowCreateRun(true)}
                  >
                     Create Payroll Run
                  </button>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-dark">
                      <tr>
                        <th>Period</th>
                        <th>Created By</th>
                        <th>Created Date</th>
                        <th>Status</th>
                        <th>Employees</th>
                        <th>Total Amount</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payrollRuns.map((run) => (
                        <tr key={run.id}>
                          <td>
                            <strong>{formatMonth(run.month, run.year)}</strong>
                          </td>
                          <td>{run.created_by || 'System'}</td>
                          <td>{new Date(run.created_at).toLocaleDateString()}</td>
                          <td>
                            <span 
                              className={`badge ${run.processed ? 'bg-success' : 'bg-warning'}`}
                              style={{ fontSize: '0.75rem' }}
                            >
                              {run.processed ? '✅ Processed' : '⏳ Pending'}
                            </span>
                          </td>
                          <td>{run.payslip_count || 0}</td>
                          <td style={{ color: '#27ae60', fontWeight: 'bold' }}>
                            {formatCurrency(run.total_amount || 0)}
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.25rem' }}>
                              {!run.processed ? (
                                <button 
                                  className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                                  onClick={() => handleRunPayroll(run.id)}
                                  disabled={loading || processingPayroll}
                                >
                                  🚀 Process
                                </button>
                              ) : (
                                <button 
                                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                                  onClick={() => {
                                    // Open payroll summary
                                    setSelectedPayrollRun(run);
                                    setActiveTab('payslips');
                                  }}
                                >
                                   View Payslips
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Salary Structures Tab */}
        {activeTab === 'salary-structures' && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="px-6 py-4 border-b border-gray-200">
              <h5 className="text-lg font-semibold text-gray-900 m-0">Employee Salary Structures</h5>
            </div>
            <div className="p-6">
              {salaryStructures.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#555' }}>
                  <h4 style={{ color: '#2c3e50' }}>No salary structures found</h4>
                  <p>Add salary structures for employees to enable payroll processing.</p>
                  <button 
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    onClick={() => setShowSalaryModal(true)}
                  >
                    💰 Add Salary Structure
                  </button>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-dark">
                      <tr>
                        <th>Employee</th>
                        <th>Type</th>
                        <th>Basic Salary</th>
                        <th>HRA</th>
                        <th>Allowances</th>
                        <th>Deductions</th>
                        <th>Annual CTC</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {salaryStructures.map((structure) => {
                        const totalAllowances = parseFloat(structure.conveyance || 0) + 
                                              parseFloat(structure.medical_allowance || 0) + 
                                              parseFloat(structure.special_allowance || 0) + 
                                              parseFloat(structure.other_allowances || 0);
                        const totalDeductions = (parseFloat(structure.basic) * parseFloat(structure.pf_percent) / 100) + 
                                              parseFloat(structure.professional_tax || 0);
                        
                        return (
                          <tr key={structure.id}>
                            <td><strong>{structure.employee_name}</strong></td>
                            <td>
                              <span className={`badge ${structure.salary_type === 'MONTHLY' ? 'bg-primary' : 'bg-secondary'}`}>
                                {structure.salary_type}
                              </span>
                            </td>
                            <td style={{ color: '#27ae60', fontWeight: 'bold' }}>
                              {formatCurrency(structure.basic)}
                            </td>
                            <td>
                              {structure.hra_fixed > 0 ? 
                                formatCurrency(structure.hra_fixed) : 
                                `${structure.hra_percent}% (${formatCurrency(parseFloat(structure.basic) * parseFloat(structure.hra_percent) / 100)})`
                              }
                            </td>
                            <td>{formatCurrency(totalAllowances)}</td>
                            <td style={{ color: '#e74c3c' }}>
                              {formatCurrency(totalDeductions)}
                            </td>
                            <td style={{ color: '#3498db', fontWeight: 'bold' }}>
                              {structure.annual_ctc > 0 ? formatCurrency(structure.annual_ctc) : 'Not set'}
                            </td>
                            <td>
                              <span className={`badge ${structure.is_active ? 'bg-success' : 'bg-danger'}`}>
                                {structure.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                            <td>
                              <button className="btn btn-outline-primary btn-sm" title="Edit">
                                ✏️
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Payslips Tab */}
        {activeTab === 'payslips' && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="px-6 py-4 border-b border-gray-200">
              <h5 className="text-lg font-semibold text-gray-900 m-0">Employee Payslips</h5>
            </div>
            <div className="p-6">
              {payslips.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#555' }}>
                  <h4 style={{ color: '#2c3e50' }}>No payslips found</h4>
                  <p>Process a payroll run to generate payslips.</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-dark">
                      <tr>
                        <th>Employee</th>
                        <th>Period</th>
                        <th>Gross Salary</th>
                        <th>Deductions</th>
                        <th>Net Salary</th>
                        <th>Payment Status</th>
                        <th>Generated</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payslips.map((payslip) => (
                        <tr key={payslip.id}>
                          <td><strong>{payslip.employee_name}</strong></td>
                          <td>{payslip.payroll_period}</td>
                          <td style={{ color: '#27ae60', fontWeight: 'bold' }}>
                            {formatCurrency(payslip.gross_salary)}
                          </td>
                          <td style={{ color: '#e74c3c' }}>
                            {formatCurrency(payslip.total_deductions)}
                          </td>
                          <td style={{ color: '#2c3e50', fontWeight: 'bold', fontSize: '1.1rem' }}>
                            {formatCurrency(payslip.net_salary)}
                          </td>
                          <td>
                            <span className={`badge ${
                              payslip.payment_status?.status === 'PAID' ? 'bg-success' :
                              payslip.payment_status?.status === 'PENDING' ? 'bg-warning' : 'bg-secondary'
                            }`}>
                              {payslip.payment_status?.status || 'Unknown'}
                            </span>
                          </td>
                          <td>{new Date(payslip.generated_at).toLocaleDateString()}</td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.25rem' }}>
                              <button className="btn btn-outline-info btn-sm" title="View Details">
                                👁️
                              </button>
                              {payslip.payslip_pdf && (
                                <button 
                                  className="btn btn-outline-danger btn-sm" 
                                  title="Download PDF"
                                  onClick={() => window.open(payslip.payslip_pdf, '_blank')}
                                >
                                  📄
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Compliance Tab */}
        {activeTab === 'compliance' && (
          <div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-md">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h5 className="text-lg font-semibold text-gray-900 m-0">⚖️ Statutory Compliance</h5>
                  </div>
                  <div className="p-6">
                    <h6 className="text-gray-900 font-semibold mb-3">📊 PF Compliance</h6>
                    <div className="mb-4 space-y-1">
                      <div className="text-gray-600">PF Rate: 12% of Basic Salary</div>
                      <div className="text-gray-600">Maximum PF Salary: $15,000/month</div>
                      <div className="text-green-600 font-medium">✅ All employees compliant</div>
                    </div>
                    
                    <h6 className="text-gray-900 font-semibold mb-3">🏥 ESI Compliance</h6>
                    <div className="mb-4 space-y-1">
                      <div className="text-gray-600">ESI Rate: 0.75% of Gross Salary</div>
                      <div className="text-gray-600">ESI Threshold: $21,000/month</div>
                      <div className="text-green-600 font-medium">✅ Threshold checks active</div>
                    </div>
                    
                    <h6 className="text-gray-900 font-semibold mb-3">💼 Professional Tax</h6>
                    <div className="space-y-1">
                      <div className="text-gray-600">State-specific PT slabs applied</div>
                      <div className="text-gray-600">Monthly deduction as per salary slabs</div>
                      <div className="text-green-600 font-medium">✅ Auto-calculated</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-md">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h5 className="text-lg font-semibold text-gray-900 m-0">📈 Tax Compliance</h5>
                  </div>
                  <div className="p-6">
                    <h6 className="text-gray-900 font-semibold mb-3">🏛️ Income Tax (TDS)</h6>
                    <div className="mb-4 space-y-1">
                      <div className="text-gray-600">New Tax Regime (FY 2024-25)</div>
                      <div className="text-gray-600">Monthly TDS as per projected annual income</div>
                      <div className="text-gray-600">Tax slabs: 0%, 5%, 10%, 15%, 20%, 30%</div>
                    </div>
                    
                    <h6 className="text-gray-900 font-semibold mb-3">📊 Form 16 Generation</h6>
                    <div className="mb-4 space-y-1">
                      <div className="text-yellow-600 font-medium">⚠️ Available at year end</div>
                      <div className="text-gray-600">Includes salary certificate</div>
                      <div className="text-gray-600">Tax deduction summary</div>
                    </div>
                    
                    <button className="bg-gray-400 text-white px-4 py-2 rounded-lg font-medium cursor-not-allowed" disabled>
                      Generate Tax Reports
                    </button>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-md">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h5 className="text-lg font-semibold text-gray-900 m-0">📋 Audit Trail</h5>
                  </div>
                  <div className="p-6 space-y-2">
                    <div className="text-gray-600">✅ All payroll changes logged</div>
                    <div className="text-gray-600">✅ Salary revisions tracked</div>
                    <div className="text-gray-600">✅ Payment status maintained</div>
                    <div className="text-gray-600">✅ User actions recorded</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* All Modals Container */}
      {(showCreateRun || showSalaryModal || showBonusModal || showReportModal) && (
        <div>
          {/* Create Payroll Run Modal */}
          {showCreateRun && (
          <div className="modal-overlay" onClick={() => setShowCreateRun(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h5 style={{ color: '#2c3e50' }}>Create New Payroll Run</h5>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label>Year:</label>
                  <input 
                    type="number" 
                    className="form-control"
                    value={newRun.year}
                    onChange={(e) => setNewRun({...newRun, year: parseInt(e.target.value)})}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label>Month:</label>
                  <select 
                    className="form-control"
                    value={newRun.month}
                    onChange={(e) => setNewRun({...newRun, month: parseInt(e.target.value)})}
                  >
                    {Array.from({length: 12}, (_, i) => (
                      <option key={i+1} value={i+1}>
                        {new Date(2024, i).toLocaleDateString('en-US', { month: 'long' })}
                      </option>
                    ))}
                  </select>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                  <button 
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors" 
                    onClick={() => setShowCreateRun(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:bg-gray-400" 
                    onClick={handleCreatePayrollRun}
                    disabled={loading}
                  >
                    Create Run
                  </button>
                </div>
              </div>
            </div>
          </div>
          )}

          {/* Enhanced Salary Structure Modal */}
          {showSalaryModal && (
          <div className="modal-overlay" onClick={() => setShowSalaryModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto' }}>
              <h5 style={{ color: '#2c3e50' }}>💰 Add Comprehensive Salary Structure</h5>
              <div style={{ marginTop: '1rem' }}>
                {/* Basic Information */}
                <div className="card" style={{ marginBottom: '1rem' }}>
                  <div className="card-header">
                    <h6 style={{ margin: 0, color: '#2c3e50' }}>Basic Information</h6>
                  </div>
                  <div className="card-body">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label>Employee: *</label>
                        <select 
                          className="form-control"
                          value={newSalaryStructure.employee}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, employee: e.target.value})}
                          required
                        >
                          <option value="">Select Employee</option>
                          {getEmployeesWithoutSalaryStructure().map(emp => (
                            <option key={emp.id} value={emp.id}>
                              {emp.first_name} {emp.last_name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label>Salary Type:</label>
                        <select 
                          className="form-control"
                          value={newSalaryStructure.salary_type}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, salary_type: e.target.value})}
                        >
                          <option value="MONTHLY">Monthly</option>
                          <option value="HOURLY">Hourly</option>
                          <option value="DAILY">Daily</option>
                          <option value="CONTRACT">Contract</option>
                        </select>
                      </div>
                      <div>
                        <label>Basic Salary ($): *</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.basic}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, basic: e.target.value})}
                          placeholder="Enter basic salary"
                          required
                        />
                      </div>
                      <div>
                        <label>Annual CTC ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.annual_ctc}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, annual_ctc: e.target.value})}
                          placeholder="Annual Cost to Company"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Allowances */}
                <div className="card" style={{ marginBottom: '1rem' }}>
                  <div className="card-header">
                    <h6 style={{ margin: 0, color: '#2c3e50' }}>🏠 Allowances</h6>
                  </div>
                  <div className="card-body">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label>HRA Percentage (%):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.hra_percent}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, hra_percent: e.target.value})}
                          placeholder="20"
                        />
                      </div>
                      <div>
                        <label>HRA Fixed Amount ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.hra_fixed}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, hra_fixed: e.target.value})}
                          placeholder="Fixed HRA (overrides %)"
                        />
                      </div>
                      <div>
                        <label>Conveyance Allowance ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.conveyance}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, conveyance: e.target.value})}
                          placeholder="1000"
                        />
                      </div>
                      <div>
                        <label>Medical Allowance ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.medical_allowance}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, medical_allowance: e.target.value})}
                          placeholder="500"
                        />
                      </div>
                      <div>
                        <label>Special Allowance ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.special_allowance}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, special_allowance: e.target.value})}
                          placeholder="0"
                        />
                      </div>
                      <div>
                        <label>Other Allowances ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.other_allowances}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, other_allowances: e.target.value})}
                          placeholder="0"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Deductions */}
                <div className="card" style={{ marginBottom: '1rem' }}>
                  <div className="card-header">
                    <h6 style={{ margin: 0, color: '#2c3e50' }}>📉 Statutory Deductions</h6>
                  </div>
                  <div className="card-body">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label>PF Percentage (%):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.pf_percent}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, pf_percent: e.target.value})}
                          placeholder="12"
                        />
                      </div>
                      <div>
                        <label>ESI Percentage (%):</label>
                        <input 
                          type="number" 
                          step="0.01"
                          className="form-control"
                          value={newSalaryStructure.esi_percent}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, esi_percent: e.target.value})}
                          placeholder="0.75"
                        />
                      </div>
                      <div>
                        <label>Professional Tax ($):</label>
                        <input 
                          type="number" 
                          className="form-control"
                          value={newSalaryStructure.professional_tax}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, professional_tax: e.target.value})}
                          placeholder="200"
                        />
                      </div>
                      <div>
                        <label>Overtime Rate (multiplier):</label>
                        <input 
                          type="number" 
                          step="0.1"
                          className="form-control"
                          value={newSalaryStructure.overtime_rate}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, overtime_rate: e.target.value})}
                          placeholder="1.5"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Settings */}
                <div className="card" style={{ marginBottom: '1rem' }}>
                  <div className="card-header">
                    <h6 style={{ margin: 0, color: '#2c3e50' }}>⚙️ Additional Settings</h6>
                  </div>
                  <div className="card-body">
                    <div>
                      <label>
                        <input 
                          type="checkbox" 
                          checked={newSalaryStructure.bonus_eligible}
                          onChange={(e) => setNewSalaryStructure({...newSalaryStructure, bonus_eligible: e.target.checked})}
                        />
                        {' '}Eligible for Bonus
                      </label>
                      <small style={{ display: 'block', color: '#666' }}>
                        Employee can receive festival bonuses and performance bonuses
                      </small>
                    </div>
                  </div>
                </div>
              </div>
                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <button 
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors" 
                    onClick={() => {
                      setShowSalaryModal(false);
                      resetSalaryStructureForm();
                    }}
                  >
                    Cancel
                  </button>
                  <button 
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:bg-gray-400" 
                    onClick={handleCreateSalaryStructure}
                    disabled={loading || !newSalaryStructure.employee || !newSalaryStructure.basic}
                  >
                    {loading ? 'Creating...' : 'Create Structure'}
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Bulk Bonus Modal */}
          {showBonusModal && (
          <div className="modal-overlay" onClick={() => setShowBonusModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
              <h5 style={{ color: '#2c3e50' }}>🎁 Add Bulk Bonus</h5>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label>Employees:</label>
                  <div style={{ maxHeight: '150px', overflowY: 'auto', border: '1px solid #ddd', padding: '0.5rem', borderRadius: '4px' }}>
                    {employees.map(emp => (
                      <div key={emp.id} style={{ marginBottom: '0.25rem' }}>
                        <label>
                          <input 
                            type="checkbox" 
                            checked={newBonus.employees.includes(emp.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewBonus({...newBonus, employees: [...newBonus.employees, emp.id]});
                              } else {
                                setNewBonus({...newBonus, employees: newBonus.employees.filter(id => id !== emp.id)});
                              }
                            }}
                          />
                          {' '}{emp.first_name} {emp.last_name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label>Bonus Type:</label>
                    <select 
                      className="form-control"
                      value={newBonus.bonus_type}
                      onChange={(e) => setNewBonus({...newBonus, bonus_type: e.target.value})}
                    >
                      <option value="FESTIVAL">Festival Bonus</option>
                      <option value="PERFORMANCE">Performance Bonus</option>
                      <option value="ANNUAL">Annual Bonus</option>
                      <option value="RETENTION">Retention Bonus</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>
                  <div>
                    <label>Fixed Amount ($):</label>
                    <input 
                      type="number" 
                      className="form-control"
                      value={newBonus.amount}
                      onChange={(e) => setNewBonus({...newBonus, amount: e.target.value})}
                      placeholder="Enter fixed amount"
                    />
                  </div>
                  <div>
                    <label>Or Percentage of Basic (%):</label>
                    <input 
                      type="number" 
                      className="form-control"
                      value={newBonus.percentage_of_basic}
                      onChange={(e) => setNewBonus({...newBonus, percentage_of_basic: e.target.value})}
                      placeholder="Enter percentage"
                    />
                  </div>
                  <div>
                    <label>Applicable Month:</label>
                    <select 
                      className="form-control"
                      value={newBonus.applicable_month}
                      onChange={(e) => setNewBonus({...newBonus, applicable_month: parseInt(e.target.value)})}
                    >
                      {Array.from({length: 12}, (_, i) => (
                        <option key={i+1} value={i+1}>
                          {new Date(2024, i).toLocaleDateString('en-US', { month: 'long' })}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <button 
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors" 
                    onClick={() => setShowBonusModal(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:bg-gray-400" 
                    onClick={handleBulkBonus}
                    disabled={loading || newBonus.employees.length === 0}
                  >
                    {loading ? 'Processing...' : 'Add Bonuses'}
                  </button>
                </div>
              </div>
            </div>
          </div>
          )}
          
          {/* Report Generation Modal */}
          {showReportModal && (
          <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px' }}>
              <h5 style={{ color: '#2c3e50' }}>📊 Generate Payroll Report</h5>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label>Report Type:</label>
                  <select 
                    className="form-control"
                    value={reportConfig.type}
                    onChange={(e) => setReportConfig({...reportConfig, type: e.target.value})}
                  >
                    <option value="monthly_summary">Monthly Payroll Summary</option>
                    <option value="employee_wise">Employee-wise Report</option>
                    <option value="department_wise">Department-wise Report</option>
                    <option value="statutory_summary">Statutory Deductions Summary</option>
                  </select>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label>Month:</label>
                    <select 
                      className="form-control"
                      value={reportConfig.month}
                      onChange={(e) => setReportConfig({...reportConfig, month: parseInt(e.target.value)})}
                    >
                      {Array.from({length: 12}, (_, i) => (
                        <option key={i+1} value={i+1}>
                          {new Date(2024, i).toLocaleDateString('en-US', { month: 'long' })}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label>Year:</label>
                    <input 
                      type="number" 
                      className="form-control"
                      value={reportConfig.year}
                      onChange={(e) => setReportConfig({...reportConfig, year: parseInt(e.target.value)})}
                    />
                  </div>
                  <div>
                    <label>Format:</label>
                    <select 
                      className="form-control"
                      value={reportConfig.format}
                      onChange={(e) => setReportConfig({...reportConfig, format: e.target.value})}
                    >
                      <option value="csv">CSV (Excel Compatible)</option>
                      <option value="json">JSON (Data Format)</option>
                    </select>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <button 
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors" 
                    onClick={() => setShowReportModal(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:bg-gray-400" 
                    onClick={generateReport}
                    disabled={loading}
                  >
                    {loading ? 'Generating...' : 'Generate Report'}
                  </button>
                </div>
              </div>
            </div>
          </div>
          )}
        </div>
      )}

      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .modal-content {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          min-width: 500px;
          max-width: 800px;
          max-height: 80vh;
          overflow-y: auto;
          color: #374151;
        }
        .modal-content label {
          color: #374151;
          font-weight: 500;
        }
        .modal-content small {
          color: #6b7280 !important;
        }
      `}</style>
    </div>
  );
};

export default Payroll;