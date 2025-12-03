import React from 'react';

const MyAttendance = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Attendance</h1>
        <button className="btn btn-primary">Clock In/Out</button>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#27ae60' }}>Present Days</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>20</div>
              <small style={{ color: '#7f8c8d' }}>This month</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#e74c3c' }}>Absent Days</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>2</div>
              <small style={{ color: '#7f8c8d' }}>This month</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#3498db' }}>Total Hours</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>176</div>
              <small style={{ color: '#7f8c8d' }}>This month</small>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header">Recent Attendance</div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Check In</th>
                  <th>Check Out</th>
                  <th>Working Hours</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>2025-11-30</td>
                  <td>09:00 AM</td>
                  <td>06:00 PM</td>
                  <td>9 hours</td>
                  <td><span style={{ color: '#27ae60', fontWeight: 'bold' }}>Present</span></td>
                </tr>
                <tr>
                  <td>2025-11-29</td>
                  <td>09:15 AM</td>
                  <td>06:00 PM</td>
                  <td>8.75 hours</td>
                  <td><span style={{ color: '#f39c12', fontWeight: 'bold' }}>Late</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyAttendance;