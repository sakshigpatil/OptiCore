import React from 'react';

const Payroll = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Payroll Management</h1>
        <button className="btn btn-primary">Process Payroll</button>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">Monthly Payroll Summary</div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div className="card">
                <div className="card-body" style={{ textAlign: 'center' }}>
                  <h3 style={{ color: '#3498db' }}>Total Salary</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>$125,000</div>
                </div>
              </div>
              <div className="card">
                <div className="card-body" style={{ textAlign: 'center' }}>
                  <h3 style={{ color: '#27ae60' }}>Processed</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>35</div>
                </div>
              </div>
              <div className="card">
                <div className="card-body" style={{ textAlign: 'center' }}>
                  <h3 style={{ color: '#f39c12' }}>Pending</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>7</div>
                </div>
              </div>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Base Salary</th>
                  <th>Overtime</th>
                  <th>Deductions</th>
                  <th>Net Pay</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>John Doe</td>
                  <td>$5,000</td>
                  <td>$200</td>
                  <td>$300</td>
                  <td>$4,900</td>
                  <td><span style={{ color: '#27ae60', fontWeight: 'bold' }}>Processed</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Payroll;