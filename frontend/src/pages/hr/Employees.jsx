import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import api from '../../services/api';

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTerminated, setShowTerminated] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [managers, setManagers] = useState([]);
  const { user } = useSelector((state) => state.auth);

  const filteredEmployees = employees.filter(emp => 
    showTerminated || emp.status === 'ACTIVE'
  );

  useEffect(() => {
    fetchEmployees();
    fetchDepartments();
    fetchManagers();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      console.log('Fetching employees...');
      const response = await api.get('/employees/');
      console.log('Employees API response:', response);
      console.log('Response status:', response.status);
      console.log('Response data:', response.data);
      
      // Handle different response formats
      const employeeData = response.results || response.data || response || [];
      console.log('Processed employee data:', employeeData);
      console.log('Is array?', Array.isArray(employeeData));
      console.log('Length:', employeeData.length);
      
      if (employeeData.length > 0) {
        console.log('First employee structure:', employeeData[0]);
        console.log('First employee user:', employeeData[0].user);
        console.log('First employee user_details:', employeeData[0].user_details);
      }
      
      setEmployees(Array.isArray(employeeData) ? employeeData : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching employees:', err);
      console.error('Error details:', err.response);
      
      if (err.response?.status === 403) {
        setError('Access denied. Please ensure you have HR or Manager permissions.');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else {
        setError(`Failed to fetch employees data: ${err.message}`);
      }
      setEmployees([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE': return '#27ae60';
      case 'INACTIVE': return '#f39c12';
      case 'TERMINATED': return '#e74c3c';
      case 'RESIGNED': return '#95a5a6';
      default: return '#27ae60';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE': return '✅';
      case 'INACTIVE': return '⏸️';
      case 'TERMINATED': return '❌';
      case 'RESIGNED': return '👋';
      default: return '✅';
    }
  };

  const formatDepartment = (department_name) => {
    return department_name || 'No Department';
  };

  const formatManagerName = (manager_name) => {
    return manager_name || 'No Manager';
  };

  const formatRole = (role) => {
    const roleMap = {
      'ADMIN_HR': 'HR Admin',
      'MANAGER': 'Manager',
      'EMPLOYEE': 'Employee'
    };
    return roleMap[role] || role || 'Employee';
  };

  const handleDeleteEmployee = async (employeeId, employeeName) => {
    const action = window.confirm(
      `Choose how to remove employee ${employeeName}:\n\n` +
      `OK - Terminate Employee (soft delete - recommended)\n` +
      `Cancel - Permanent Delete (hard delete - cannot be undone)\n\n` +
      `Click OK for termination or Cancel for permanent deletion:`
    );

    const confirmAction = window.confirm(
      action 
        ? `Confirm: Terminate employee ${employeeName}? They will be marked as terminated but data will be preserved.`
        : `Confirm: PERMANENTLY DELETE employee ${employeeName}? This action cannot be undone and all data will be lost.`
    );

    if (!confirmAction) {
      return;
    }

    try {
      if (action) {
        // Soft delete - terminate employee
        const terminationDate = new Date().toISOString().split('T')[0]; // Today's date
        await api.post(`/employees/${employeeId}/terminate/`, {
          termination_date: terminationDate,
          reason: 'Terminated by HR Administrator'
        });
        
        // Update employee status in local state
        setEmployees(employees.map(emp => 
          emp.id === employeeId 
            ? { ...emp, status: 'TERMINATED', termination_date: terminationDate }
            : emp
        ));
        
        alert(`Employee ${employeeName} has been successfully terminated.`);
      } else {
        // Hard delete
        await api.delete(`/employees/${employeeId}/`);
        
        // Remove employee from local state
        setEmployees(employees.filter(emp => emp.id !== employeeId));
        
        alert(`Employee ${employeeName} has been permanently deleted.`);
      }
      
    } catch (err) {
      console.error('Error processing employee removal:', err);
      
      if (err.response?.status === 403) {
        alert('Access denied. You do not have permission to delete employees.');
      } else if (err.response?.status === 404) {
        alert('Employee not found. It may have already been deleted.');
      } else {
        alert(`Failed to process employee removal: ${err.message}`);
      }
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/departments/');
      setDepartments(response.results || response.data || response || []);
    } catch (err) {
      console.error('Error fetching departments:', err);
    }
  };

  const fetchManagers = async () => {
    try {
      const response = await api.get('/employees/');
      const employeeData = response.results || response.data || response || [];
      // Filter for active managers and HR admins only
      const managerList = employeeData.filter(emp => 
        (emp.user_details?.role === 'MANAGER' || emp.user_details?.role === 'ADMIN_HR') &&
        emp.status === 'ACTIVE'
      );
      setManagers(managerList);
    } catch (err) {
      console.error('Error fetching managers:', err);
    }
  };

  const handleAddEmployee = () => {
    setShowAddModal(true);
    // Refresh managers list to ensure terminated employees are excluded
    fetchManagers();
  };

  const handleEditEmployee = (employeeId, employeeName) => {
    // TODO: Implement edit functionality
    alert(`Edit functionality for ${employeeName} will be implemented soon.`);
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">Employee Management</h1>
          <button className="btn btn-primary">Add New Employee</button>
        </div>
        <div className="page-content">
          <div className="card">
            <div className="card-header">All Employees</div>
            <div className="card-body">
              <div className="loading-spinner" style={{ textAlign: 'center', padding: '2rem' }}>
                Loading employees...
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Employee Management</h1>
        <button className="btn btn-primary" onClick={handleAddEmployee}>
          Add New Employee
        </button>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">
            All Employees ({filteredEmployees.length} of {employees.length})
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                <input 
                  type="checkbox" 
                  checked={showTerminated}
                  onChange={(e) => setShowTerminated(e.target.checked)}
                />
                Show Terminated
              </label>
              <button 
                onClick={fetchEmployees} 
                className="btn btn-secondary" 
                style={{ fontSize: '0.9rem' }}
              >
                🔄 Refresh
              </button>
            </div>
          </div>
          <div className="card-body">
            {error && (
              <div className="alert alert-error" style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: '#fee', color: '#c33', borderRadius: '4px' }}>
                {error}
              </div>
            )}
            
            {filteredEmployees.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                {employees.length === 0 ? 'No employees found.' : 'No employees match the current filter.'}
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Employee ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Department</th>
                      <th>Position</th>
                      <th>Manager</th>
                      <th>Salary</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEmployees.map((employee) => (
                      <tr key={employee.id || employee.employee_id}>
                        <td><strong>{employee.employee_id}</strong></td>
                        <td>
                          <div>
                            <div style={{ fontWeight: 'bold' }}>
                              {employee.user_details?.first_name || employee.user?.first_name || ''} {employee.user_details?.last_name || employee.user?.last_name || ''}
                            </div>
                            <div style={{ fontSize: '0.85rem', color: '#666' }}>
                              {formatRole(employee.user_details?.role || employee.user?.role)}
                            </div>
                          </div>
                        </td>
                        <td>{employee.user_details?.email || employee.user?.email || 'No Email'}</td>
                        <td>{formatDepartment(employee.department_name)}</td>
                        <td>{employee.position}</td>
                        <td>{formatManagerName(employee.manager_name)}</td>
                        <td>
                          {employee.salary ? `$${parseFloat(employee.salary).toLocaleString()}` : 'N/A'}
                        </td>
                        <td>
                          <span 
                            style={{ 
                              color: getStatusColor(employee.status), 
                              fontWeight: 'bold',
                              fontSize: '0.9rem',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem'
                            }}
                          >
                            {getStatusIcon(employee.status)}
                            {employee.status || 'ACTIVE'}
                          </span>
                        </td>
                        <td>
                          <button 
                            className="btn btn-secondary" 
                            style={{ marginRight: '0.5rem', fontSize: '0.85rem' }}
                            onClick={() => handleEditEmployee(
                              employee.id, 
                              `${employee.user_details?.first_name || employee.user?.first_name || ''} ${employee.user_details?.last_name || employee.user?.last_name || ''}`
                            )}
                          >
                            Edit
                          </button>
                          <button 
                            className="btn btn-danger"
                            style={{ fontSize: '0.85rem' }}
                            onClick={() => handleDeleteEmployee(
                              employee.id,
                              `${employee.user_details?.first_name || employee.user?.first_name || ''} ${employee.user_details?.last_name || employee.user?.last_name || ''}`
                            )}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Employee Modal */}
      {showAddModal && (
        <AddEmployeeModal 
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            fetchEmployees();
          }}
          departments={departments}
          managers={managers}
        />
      )}
    </div>
  );
};

// Add Employee Modal Component
const AddEmployeeModal = ({ isOpen, onClose, onSuccess, departments, managers }) => {
  const [formData, setFormData] = useState({
    // User data
    first_name: '',
    last_name: '',
    email: '',
    username: '',
    password: 'TempPass123!', // Default strong password
    role: 'EMPLOYEE',
    phone: '',
    // Employee data
    employee_id: '',
    position: '',
    hire_date: new Date().toISOString().split('T')[0],
    salary: '',
    address: '',
    date_of_birth: '',
    department: '',
    manager: '',
    emergency_contact_name: '',
    emergency_contact_phone: ''
  });
  
  // Fetch next employee ID suggestion
  useEffect(() => {
    const fetchNextEmployeeId = async () => {
      try {
        const response = await api.get('/employees/');
        const employees = response.data.results || response.data;
        
        // Find the highest employee ID number (handle both EMP001 and EMP0001 formats)
        let maxId = 0;
        employees.forEach(emp => {
          // Match both formats: EMP001, EMP0001, etc.
          const match = emp.employee_id.match(/EMP0*(\d+)/);
          if (match) {
            const num = parseInt(match[1]);
            if (num > maxId) maxId = num;
          }
        });
        
        // Use EMP001 format (3 digits) for consistency
        const nextId = `EMP${String(maxId + 1).padStart(3, '0')}`;
        setFormData(prev => ({
          ...prev,
          employee_id: nextId
        }));
      } catch (error) {
        console.error('Error fetching employees:', error);
        // Fallback to EMP001 if can't fetch
        setFormData(prev => ({
          ...prev,
          employee_id: 'EMP001'
        }));
      }
    };
    
    if (isOpen && !formData.employee_id) {
      fetchNextEmployeeId();
    }
  }, [isOpen]);
  
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Auto-generate username from email
    if (name === 'email') {
      const baseUsername = value.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, '');
      // Add a timestamp suffix to make it more unique
      const timestamp = Date.now().toString().slice(-4);
      const username = baseUsername + timestamp;
      setFormData(prev => ({
        ...prev,
        username: username
      }));
    }
    
    // Clear field-specific error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // User data validation
    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.username.trim()) newErrors.username = 'Username is required';
    if (!formData.password.trim()) newErrors.password = 'Password is required';
    
    // Employee data validation
    if (!formData.employee_id.trim()) newErrors.employee_id = 'Employee ID is required';
    if (!formData.position.trim()) newErrors.position = 'Position is required';
    if (!formData.salary) newErrors.salary = 'Salary is required';
    if (!formData.hire_date) newErrors.hire_date = 'Hire date is required';
    
    // Format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    // Employee ID format validation
    const empIdRegex = /^EMP\d{3}$/;
    if (formData.employee_id && !empIdRegex.test(formData.employee_id)) {
      newErrors.employee_id = 'Employee ID must be in format EMP001, EMP002, etc.';
    }
    
    // Password strength validation
    if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters long';
    }
    
    // Salary validation
    if (formData.salary && (isNaN(formData.salary) || parseFloat(formData.salary) <= 0)) {
      newErrors.salary = 'Salary must be a positive number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setSaving(true);
    
    try {
      const payload = {
        user_data: {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          username: formData.username,
          password: formData.password,
          role: formData.role,
          phone: formData.phone || null
        },
        employee_id: formData.employee_id,
        position: formData.position,
        hire_date: formData.hire_date,
        salary: parseFloat(formData.salary),
        address: formData.address || null,
        date_of_birth: formData.date_of_birth || null,
        department: formData.department || null,
        manager: formData.manager || null,
        emergency_contact_name: formData.emergency_contact_name || null,
        emergency_contact_phone: formData.emergency_contact_phone || null
      };

      console.log('Creating employee with payload:', payload);
      console.log('Payload stringified:', JSON.stringify(payload, null, 2));
      
      const response = await api.post('/employees/', payload);
      console.log('Success response:', response);
      
      alert(`Employee ${formData.first_name} ${formData.last_name} created successfully!`);
      onSuccess();
      
    } catch (err) {
      console.error('Error creating employee:', err);
      console.error('Error response:', err.response?.data);
      
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Check if we got an HTML error page instead of JSON
        if (typeof errorData === 'string' && errorData.includes('<!DOCTYPE')) {
          alert('Server Error: The server returned an HTML error page. Please check the Django server logs for details.');
          console.error('HTML error page received:', errorData);
          return;
        }
        
        let errorMessage = 'Failed to create employee:\n\n';
        
        // Handle user_data validation errors
        if (errorData.user_data && typeof errorData.user_data === 'object') {
          errorMessage += 'User Information Errors:\n';
          Object.entries(errorData.user_data).forEach(([key, value]) => {
            const fieldName = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            const errorText = Array.isArray(value) ? value.join(', ') : value;
            errorMessage += `• ${fieldName}: ${errorText}\n`;
          });
          errorMessage += '\n';
        }
        
        // Handle other field errors
        if (typeof errorData === 'object' && !Array.isArray(errorData)) {
          Object.entries(errorData).forEach(([key, value]) => {
            if (key !== 'user_data' && key !== 'non_field_errors') {
              const fieldName = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
              const errorText = Array.isArray(value) ? value.join(', ') : value;
              errorMessage += `• ${fieldName}: ${errorText}\n`;
            }
          });
        }
        
        // Handle general errors
        if (errorData.non_field_errors) {
          errorMessage += '\nGeneral Errors:\n';
          errorData.non_field_errors.forEach(error => {
            errorMessage += `• ${error}\n`;
          });
        }
        
        // If we couldn't parse the error properly, show raw response
        if (errorMessage === 'Failed to create employee:\n\n') {
          errorMessage += 'Raw server response:\n';
          errorMessage += typeof errorData === 'string' ? errorData : JSON.stringify(errorData, null, 2);
        }
        
        alert(errorMessage);
      } else if (err.response?.status === 403) {
        alert('Access Denied: You do not have permission to create employees.');
      } else if (err.response?.status === 500) {
        alert('Server Error: Please try again later or contact IT support.');
      } else {
        alert(`Failed to create employee: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div className="modal-content" style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        width: '90%',
        maxWidth: '600px',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <div className="modal-header" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          borderBottom: '1px solid #eee',
          paddingBottom: '1rem'
        }}>
          <h2>Add New Employee</h2>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>First Name *</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              {errors.first_name && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.first_name}</div>}
            </div>
            
            <div>
              <label>Last Name *</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              {errors.last_name && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.last_name}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Email *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="john.doe@company.com"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              {errors.email && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.email}</div>}
            </div>
            
            <div>
              <label>Username *</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Auto-generated from email"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f9f9f9' }}
                readOnly
              />
              {errors.username && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.username}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Employee ID *</label>
              <input
                type="text"
                name="employee_id"
                value={formData.employee_id}
                onChange={handleInputChange}
                placeholder="e.g., EMP007"
                style={{ 
                  width: '100%', 
                  padding: '0.5rem', 
                  border: '1px solid #ddd', 
                  borderRadius: '4px',
                  backgroundColor: formData.employee_id && formData.employee_id.startsWith('EMP') ? '#f0f8ff' : 'white'
                }}
              />
              {!formData.employee_id && (
                <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                  Auto-suggesting next available ID...
                </div>
              )}
              {errors.employee_id && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.employee_id}</div>}
            </div>
            
            <div>
              <label>Position *</label>
              <input
                type="text"
                name="position"
                value={formData.position}
                onChange={handleInputChange}
                placeholder="e.g., Software Developer"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              {errors.position && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.position}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Temporary Password *</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Temporary password for new user"
                  style={{ width: '100%', padding: '0.5rem', paddingRight: '2.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '0.5rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    border: 'none',
                    background: 'none',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    color: '#666'
                  }}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                User can change this after first login
              </div>
              {errors.password && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.password}</div>}
            </div>
            
            <div>
              <label>Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value="EMPLOYEE">Employee</option>
                <option value="MANAGER">Manager</option>
                <option value="ADMIN_HR">HR Admin</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Department</label>
              <select
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value="">Select Department</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label>Manager</label>
              <select
                name="manager"
                value={formData.manager}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value="">Select Manager (Active Only)</option>
                {managers.map(mgr => (
                  <option key={mgr.id} value={mgr.id}>
                    {mgr.user_details?.first_name} {mgr.user_details?.last_name} ({mgr.employee_id})
                  </option>
                ))}
              </select>
              {managers.length === 0 && (
                <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                  No active managers available
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Salary *</label>
              <input
                type="number"
                name="salary"
                value={formData.salary}
                onChange={handleInputChange}
                placeholder="e.g., 50000"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              {errors.salary && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.salary}</div>}
            </div>
            
            <div>
              <label>Hire Date *</label>
              <input
                type="date"
                name="hire_date"
                value={formData.hire_date}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              {errors.hire_date && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.hire_date}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+1234567890"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            
            <div>
              <label>Date of Birth</label>
              <input
                type="date"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              rows="2"
              placeholder="Employee address"
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>Emergency Contact Name</label>
              <input
                type="text"
                name="emergency_contact_name"
                value={formData.emergency_contact_name}
                onChange={handleInputChange}
                placeholder="Emergency contact full name"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            
            <div>
              <label>Emergency Contact Phone</label>
              <input
                type="tel"
                name="emergency_contact_phone"
                value={formData.emergency_contact_phone}
                onChange={handleInputChange}
                placeholder="+1234567890"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '0.75rem 1.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                background: 'white',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              style={{
                padding: '0.75rem 1.5rem',
                border: 'none',
                borderRadius: '4px',
                background: saving ? '#ccc' : '#007bff',
                color: 'white',
                cursor: saving ? 'not-allowed' : 'pointer'
              }}
            >
              {saving ? 'Creating...' : 'Create Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Employees;