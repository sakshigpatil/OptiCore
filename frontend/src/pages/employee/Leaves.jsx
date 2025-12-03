import React from 'react';

const MyLeaves = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Leave Requests</h1>
        <button className="btn btn-primary">Request Leave</button>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#3498db' }}>Total Leave</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>25</div>
              <small style={{ color: '#7f8c8d' }}>days/year</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#27ae60' }}>Used</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>7</div>
              <small style={{ color: '#7f8c8d' }}>days</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#f39c12' }}>Remaining</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>18</div>
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
                <tr>
                  <td>Annual Leave</td>
                  <td>2025-01-15</td>
                  <td>2025-01-19</td>
                  <td>5</td>
                  <td>Family vacation</td>
                  <td><span style={{ color: '#f39c12', fontWeight: 'bold' }}>Pending</span></td>
                </tr>
                <tr>
                  <td>Sick Leave</td>
                  <td>2025-11-20</td>
                  <td>2025-11-22</td>
                  <td>3</td>
                  <td>Medical appointment</td>
                  <td><span style={{ color: '#27ae60', fontWeight: 'bold' }}>Approved</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyLeaves;