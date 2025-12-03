import React from 'react';

const Leaves = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Leave Management</h1>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">Pending Leave Requests</div>
          <div className="card-body">
            <table className="table">
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
                <tr>
                  <td>John Doe</td>
                  <td>Annual Leave</td>
                  <td>2025-01-15</td>
                  <td>2025-01-19</td>
                  <td>5</td>
                  <td>Family vacation</td>
                  <td>
                    <button className="btn btn-success" style={{ marginRight: '0.5rem' }}>Approve</button>
                    <button className="btn btn-danger">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaves;