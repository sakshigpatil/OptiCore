import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const MyLeaves = () => {
  const [leaves, setLeaves] = useState([]);
  const [leaveBalance, setLeaveBalance] = useState({
    total: 25,
    used: 0,
    remaining: 25
  });
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    leave_type: '',
    start_date: '',
    end_date: '',
    reason: ''
  });

  useEffect(() => {
    fetchLeaves();
  }, []);

  // Recalculate leave balance when leaves data changes
  useEffect(() => {
    if (leaves.length > 0) {
      fetchLeaveBalance();
    }
  }, [leaves]);

  const fetchLeaves = async () => {
    try {
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      const response = await api.get(`/leaves/leave-requests/?t=${timestamp}`);
      console.log('Leave requests response:', response);
      
      // The API service returns response.data, so we should have the pagination structure directly
      let leaveData = [];
      if (response && response.results) {
        leaveData = response.results;
      } else if (Array.isArray(response)) {
        leaveData = response;
      } else {
        console.warn('Unexpected response structure:', response);
        leaveData = [];
      }
      
      console.log('Parsed leave data:', leaveData);
      setLeaves(leaveData);
    } catch (error) {
      console.error('Error fetching leaves:', error);
      console.error('Error details:', error.response?.data);
      
      // Don't set dummy data - let user know there's an issue
      setLeaves([]);
      alert('Failed to load leave requests. Please refresh the page.');
    }
  };

  const fetchLeaveBalance = async () => {
    try {
      const response = await api.get('/leaves/leave-requests/balance/');
      console.log('Leave balance response:', response);
      
      const balanceData = response.data || response;
      setLeaveBalance(balanceData);
    } catch (error) {
      console.error('Error fetching leave balance:', error);
      
      // Calculate from existing leaves (approved ones only)
      const approvedLeaves = leaves.filter(leave => leave.status === 'APPROVED');
      const usedDays = approvedLeaves.reduce((total, leave) => total + (leave.days_requested || 0), 0);
      
      setLeaveBalance({
        total: 25,
        used: usedDays,
        remaining: 25 - usedDays
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const submitData = {
        leave_type: parseInt(formData.leave_type), // Convert to integer
        start_date: formData.start_date,
        end_date: formData.end_date,
        reason: formData.reason,
        days_requested: calculateDays()
      };
      
      console.log('Submitting leave request:', submitData);
      const response = await api.post('/leaves/leave-requests/', submitData);
      console.log('Leave request response:', response);
      
      setShowModal(false);
      setFormData({
        leave_type: '',
        start_date: '',
        end_date: '',
        reason: ''
      });
      
      // Refresh data after successful submission
      await fetchLeaves();
      
      alert('Leave request submitted successfully!');
    } catch (error) {
      console.error('Error submitting leave request:', error);
      
      // Show more detailed error message
      let errorMessage = 'Error submitting leave request. Please try again.';
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else {
          // Show field-specific errors
          const fieldErrors = [];
          Object.keys(error.response.data).forEach(field => {
            const fieldError = error.response.data[field];
            if (Array.isArray(fieldError)) {
              fieldErrors.push(`${field}: ${fieldError.join(', ')}`);
            } else {
              fieldErrors.push(`${field}: ${fieldError}`);
            }
          });
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join('\n');
          }
        }
      }
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const calculateDays = () => {
    if (formData.start_date && formData.end_date) {
      const start = new Date(formData.start_date);
      const end = new Date(formData.end_date);
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      return diffDays;
    }
    return 0;
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Leave Requests</h1>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            className="btn btn-secondary"
            onClick={fetchLeaves}
            disabled={loading}
          >
            🔄 Refresh
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowModal(true)}
          >
            Request Leave
          </button>
        </div>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#3498db' }}>Total Leave</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{leaveBalance.total}</div>
              <small style={{ color: '#7f8c8d' }}>days/year</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#27ae60' }}>Used</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{leaveBalance.used}</div>
              <small style={{ color: '#7f8c8d' }}>days</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#f39c12' }}>Remaining</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{leaveBalance.remaining}</div>
              <small style={{ color: '#7f8c8d' }}>days</small>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header">Leave History</div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Leave Type</th>
                  <th>From Date</th>
                  <th>To Date</th>
                  <th>Days</th>
                  <th>Reason</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {leaves.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                      No leave requests found. Click "Request Leave" to submit your first request.
                    </td>
                  </tr>
                ) : (
                  leaves.map((leave, index) => (
                    <tr key={leave.id || index}>
                      <td>{leave.leave_type_detail?.name || leave.leave_type_name || leave.leave_type?.name || 'Unknown'}</td>
                      <td>{new Date(leave.start_date).toLocaleDateString()}</td>
                      <td>{new Date(leave.end_date).toLocaleDateString()}</td>
                      <td>{leave.days_requested}</td>
                      <td style={{ maxWidth: '200px', wordWrap: 'break-word' }}>{leave.reason}</td>
                      <td>
                        <span style={{ 
                          color: leave.status === 'APPROVED' ? '#27ae60' : 
                                leave.status === 'REJECTED' ? '#e74c3c' : 
                                leave.status === 'PENDING' ? '#f39c12' : '#666', 
                          fontWeight: 'bold' 
                        }}>
                          {leave.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Leave Request Modal */}
        {showModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1050
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              width: '90%',
              maxWidth: '500px',
              maxHeight: '90vh',
              overflow: 'auto'
            }}>
              <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #dee2e6' }}>
                <h5 style={{ margin: 0 }}>Request Leave</h5>
              </div>
              
              <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label className="form-label">Leave Type *</label>
                  <select
                    name="leave_type"
                    value={formData.leave_type}
                    onChange={handleInputChange}
                    className="form-control"
                    required
                  >
                    <option value="">Select leave type</option>
                    <option value="1">Annual Leave</option>
                    <option value="2">Sick Leave</option>
                    <option value="3">Personal Leave</option>
                    <option value="4">Maternity Leave</option>
                    <option value="5">Paternity Leave</option>
                    <option value="6">Emergency Leave</option>
                  </select>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label className="form-label">Start Date *</label>
                    <input
                      type="date"
                      name="start_date"
                      value={formData.start_date}
                      onChange={handleInputChange}
                      className="form-control"
                      min={new Date().toISOString().split('T')[0]}
                      required
                    />
                  </div>
                  <div>
                    <label className="form-label">End Date *</label>
                    <input
                      type="date"
                      name="end_date"
                      value={formData.end_date}
                      onChange={handleInputChange}
                      className="form-control"
                      min={formData.start_date || new Date().toISOString().split('T')[0]}
                      required
                    />
                  </div>
                </div>

                {formData.start_date && formData.end_date && (
                  <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                    <small>
                      <strong>Duration:</strong> {calculateDays()} day{calculateDays() !== 1 ? 's' : ''}
                    </small>
                  </div>
                )}

                <div style={{ marginBottom: '1rem' }}>
                  <label className="form-label">Reason *</label>
                  <textarea
                    name="reason"
                    value={formData.reason}
                    onChange={handleInputChange}
                    className="form-control"
                    rows="3"
                    placeholder="Please provide reason for leave"
                    required
                  />
                </div>



                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowModal(false);
                      setFormData({
                        leave_type: '',
                        start_date: '',
                        end_date: '',
                        reason: ''
                      });
                    }}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Submitting...' : 'Submit Request'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyLeaves;