import React from 'react';

const Attendance = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Attendance Management</h1>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">Today's Attendance</div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div className="card">
                <div className="card-body" style={{ textAlign: 'center' }}>
                  <h3 style={{ color: '#27ae60' }}>Present</h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>38</div>
                </div>
              </div>
              <div className="card">
                <div className="card-body" style={{ textAlign: 'center' }}>
                  <h3 style={{ color: '#e74c3c' }}>Absent</h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>4</div>
                </div>
              </div>
              <div className="card">
                <div className="card-body" style={{ textAlign: 'center' }}>
                  <h3 style={{ color: '#f39c12' }}>Late</h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>2</div>
                </div>
              </div>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Check In</th>
                  <th>Check Out</th>
                  <th>Working Hours</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>John Doe</td>
                  <td>09:00 AM</td>
                  <td>06:00 PM</td>
                  <td>9 hours</td>
                  <td><span style={{ color: '#27ae60', fontWeight: 'bold' }}>Present</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Attendance;