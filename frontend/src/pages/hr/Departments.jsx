import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';

const Departments = () => {
  const [departments, setDepartments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    head: ''
  });

  useEffect(() => {
    fetchDepartments();
    fetchEmployees();
  }, []);

  const fetchDepartments = async () => {
    try {
      setLoading(true);
      const response = await api.get('/departments/');
      const departmentsList = response.results || response || [];
      setDepartments(departmentsList);
    } catch (error) {
      console.error('Error fetching departments:', error);
      toast.error('Failed to fetch departments');
      setDepartments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/employees/');
      const employeesList = response.results || response || [];
      setEmployees(employeesList);
    } catch (error) {
      console.error('Error fetching employees:', error);
      setEmployees([]);
    }
  };

  const handleAddDepartment = () => {
    setEditingDepartment(null);
    setFormData({ name: '', description: '', head: '' });
    setShowModal(true);
  };

  const handleEditDepartment = (department) => {
    setEditingDepartment(department);
    setFormData({
      name: department.name,
      description: department.description || '',
      head: department.head || ''
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error('Department name is required');
      return;
    }

    try {
      const submitData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        head: formData.head || null
      };

      if (editingDepartment) {
        // Update existing department
        await api.put(`/departments/${editingDepartment.id}/`, submitData);
        toast.success('Department updated successfully');
      } else {
        // Create new department
        await api.post('/departments/', submitData);
        toast.success('Department created successfully');
      }
      
      setShowModal(false);
      fetchDepartments();
    } catch (error) {
      console.error('Error saving department:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          'Failed to save department';
      toast.error(errorMessage);
    }
  };

  const handleDeleteDepartment = async (departmentId) => {
    if (!window.confirm('Are you sure you want to delete this department?')) {
      return;
    }

    try {
      await api.delete(`/departments/${departmentId}/`);
      toast.success('Department deleted successfully');
      fetchDepartments();
    } catch (error) {
      console.error('Error deleting department:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          'Failed to delete department';
      toast.error(errorMessage);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">Department Management</h1>
        </div>
        <div className="page-content">
          <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading departments...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Department Management</h1>
        <button className="btn btn-primary" onClick={handleAddDepartment}>
          <i className="fas fa-plus me-1"></i>
          Add Department
        </button>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span>All Departments</span>
            <button className="btn btn-secondary btn-sm" onClick={fetchDepartments}>
              <i className="fas fa-sync-alt me-1"></i>
              Refresh
            </button>
          </div>
          <div className="card-body">
            {departments.length === 0 ? (
              <div className="text-center py-4">
                <i className="fas fa-building fa-3x text-muted mb-3"></i>
                <h5 className="text-muted">No Departments Found</h5>
                <p className="text-muted">Start by creating your first department.</p>
                <button className="btn btn-primary" onClick={handleAddDepartment}>
                  <i className="fas fa-plus me-1"></i>
                  Add Department
                </button>
              </div>
            ) : (
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
                gap: '1.5rem' 
              }}>
                {departments.map((department) => (
                  <div key={department.id} className="card">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <h3 className="mb-0">{department.name}</h3>
                        <div className="d-flex gap-2">
                          <button 
                            className="btn btn-sm btn-outline-primary" 
                            onClick={() => handleEditDepartment(department)}
                            title="Edit Department"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button 
                            className="btn btn-sm btn-outline-danger" 
                            onClick={() => handleDeleteDepartment(department.id)}
                            title="Delete Department"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                      
                      {department.description && (
                        <p className="text-muted mb-3">{department.description}</p>
                      )}
                      
                      <div className="mb-2">
                        <strong>Employees:</strong> 
                        <span className="badge bg-primary ms-2">{department.employee_count}</span>
                      </div>
                      
                      <div>
                        <strong>Head:</strong> 
                        <span className="ms-2">
                          {department.head_name || 'Not assigned'}
                        </span>
                      </div>
                      
                      <div className="mt-2">
                        <small className="text-muted">
                          Created: {new Date(department.created_at).toLocaleDateString()}
                        </small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add/Edit Department Modal */}
      {showModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingDepartment ? 'Edit Department' : 'Add New Department'}
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label htmlFor="name" className="form-label">Department Name *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      placeholder="Enter department name"
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="description" className="form-label">Description</label>
                    <textarea 
                      className="form-control" 
                      id="description"
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows="3"
                      placeholder="Enter department description"
                    ></textarea>
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="head" className="form-label">Department Head</label>
                    <select 
                      className="form-control" 
                      id="head"
                      name="head"
                      value={formData.head}
                      onChange={handleInputChange}
                    >
                      <option value="">Select department head</option>
                      {employees.map((employee) => (
                        <option key={employee.id} value={employee.id}>
                          {employee.user_details?.first_name} {employee.user_details?.last_name} 
                          ({employee.employee_id})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => setShowModal(false)}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingDepartment ? 'Update' : 'Create'} Department
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Departments;