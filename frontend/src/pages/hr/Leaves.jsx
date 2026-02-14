import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';

const Leaves = () => {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    fetchLeaveRequests();
  }, []);

  const fetchLeaveRequests = async () => {
    try {
      setLoading(true);
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      const response = await api.get(`/leaves/leave-requests/?t=${timestamp}`);
      console.log('HR/Manager Leave Requests Response:', response);
      
      const requests = response.results || response || [];
      console.log('Total leave requests:', requests.length);
      
      // Filter to show only pending requests
      const pendingRequests = requests.filter(req => req.status === 'PENDING');
      console.log('Pending leave requests:', pendingRequests.length);
      
      setLeaveRequests(pendingRequests);
    } catch (error) {
      console.error('Error fetching leave requests:', error);
      toast.error('Failed to fetch leave requests');
      setLeaveRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (leaveId) => {
    try {
      setProcessingId(leaveId);
      await api.post(`/leaves/leave-requests/${leaveId}/approve/`);
      toast.success('Leave request approved successfully');
      // Remove from list after approval
      setLeaveRequests(prev => prev.filter(req => req.id !== leaveId));
    } catch (error) {
      console.error('Error approving leave:', error);
      const errorMessage = error.response?.data?.error || 'Failed to approve leave request';
      toast.error(errorMessage);
    } finally {
      setProcessingId(null);
    }
  };

  const handleRejectClick = (leave) => {
    setSelectedLeave(leave);
    setRejectionReason('');
    setShowRejectModal(true);
  };

  const handleRejectConfirm = async () => {
    try {
      setProcessingId(selectedLeave.id);
      await api.post(`/leaves/leave-requests/${selectedLeave.id}/reject/`, {
        rejection_reason: rejectionReason
      });
      toast.success('Leave request rejected successfully');
      // Remove from list after rejection
      setLeaveRequests(prev => prev.filter(req => req.id !== selectedLeave.id));
      setShowRejectModal(false);
    } catch (error) {
      console.error('Error rejecting leave:', error);
      const errorMessage = error.response?.data?.error || 'Failed to reject leave request';
      toast.error(errorMessage);
    } finally {
      setProcessingId(null);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">Leave Management</h1>
        </div>
        <div className="page-content">
          <div className="d-flex justify-content-center align-items-center" style={{ height: '300px' }}>
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading leave requests...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Leave Management</h1>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span>Pending Leave Requests</span>
            <button className="btn btn-primary btn-sm" onClick={fetchLeaveRequests}>
              <i className="fas fa-sync-alt"></i> Refresh
            </button>
          </div>
          <div className="card-body">
            {leaveRequests.length === 0 ? (
              <div className="text-center py-4">
                <i className="fas fa-calendar-check fa-3x text-muted mb-3"></i>
                <h5 className="text-muted">No Pending Leave Requests</h5>
                <p className="text-muted">All leave requests have been processed.</p>
              </div>
            ) : (
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Leave Type</th>
                    <th>From Date</th>
                    <th>To Date</th>
                    <th>Days</th>
                    <th>Reason</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {leaveRequests.map((leave) => (
                    <tr key={leave.id}>
                      <td>
                        <div>
                          <strong>
                            {leave.employee_detail?.user?.first_name || leave.employee?.user?.first_name || 'Unknown'} {' '}
                            {leave.employee_detail?.user?.last_name || leave.employee?.user?.last_name || 'User'}
                          </strong>
                          <br />
                          <small className="text-muted">
                            {leave.employee_detail?.employee_id || leave.employee?.employee_id || 'N/A'}
                          </small>
                        </div>
                      </td>
                      <td>
                        <span className="badge bg-info">
                          {leave.leave_type_detail?.name || leave.leave_type?.name || leave.leave_type_name || 'Unknown'}
                        </span>
                      </td>
                      <td>{formatDate(leave.start_date)}</td>
                      <td>{formatDate(leave.end_date)}</td>
                      <td>
                        <span className="badge bg-secondary">{leave.days_requested} day{leave.days_requested > 1 ? 's' : ''}</span>
                      </td>
                      <td>
                        <span title={leave.reason}>
                          {leave.reason.length > 50 ? `${leave.reason.substring(0, 50)}...` : leave.reason}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="btn btn-success btn-sm me-2" 
                          onClick={() => handleApprove(leave.id)}
                          disabled={processingId === leave.id}
                        >
                          {processingId === leave.id ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                              Approving...
                            </>
                          ) : (
                            <>
                              <i className="fas fa-check me-1"></i>
                              Approve
                            </>
                          )}
                        </button>
                        <button 
                          className="btn btn-danger btn-sm" 
                          onClick={() => handleRejectClick(leave)}
                          disabled={processingId === leave.id}
                        >
                          <i className="fas fa-times me-1"></i>
                          Reject
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Reject Leave Request</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowRejectModal(false)}
                  disabled={processingId === selectedLeave?.id}
                ></button>
              </div>
              <div className="modal-body">
                <p><strong>Employee:</strong> {selectedLeave?.employee_detail?.user?.first_name || selectedLeave?.employee?.user?.first_name} {selectedLeave?.employee_detail?.user?.last_name || selectedLeave?.employee?.user?.last_name}</p>
                <p><strong>Leave Type:</strong> {selectedLeave?.leave_type_detail?.name || selectedLeave?.leave_type?.name || selectedLeave?.leave_type_name}</p>
                <p><strong>Duration:</strong> {formatDate(selectedLeave?.start_date)} to {formatDate(selectedLeave?.end_date)} ({selectedLeave?.days_requested} days)</p>
                <p><strong>Reason:</strong> {selectedLeave?.reason}</p>
                
                <div className="mb-3">
                  <label htmlFor="rejectionReason" className="form-label">Rejection Reason *</label>
                  <textarea 
                    className="form-control" 
                    id="rejectionReason" 
                    rows="3" 
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Please provide a reason for rejection..."
                    required
                  ></textarea>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowRejectModal(false)}
                  disabled={processingId === selectedLeave?.id}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-danger" 
                  onClick={handleRejectConfirm}
                  disabled={!rejectionReason.trim() || processingId === selectedLeave?.id}
                >
                  {processingId === selectedLeave?.id ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                      Rejecting...
                    </>
                  ) : (
                    'Reject Leave Request'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Leaves;