import React from 'react';

const Payslip = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Payslips</h1>
        <button className="btn btn-primary">Download Current</button>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">Current Month Payslip - November 2025</div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div>
                <h4>Earnings</h4>
                <table className="table">
                  <tbody>
                    <tr>
                      <td>Basic Salary</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$4,000</td>
                    </tr>
                    <tr>
                      <td>House Allowance</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$800</td>
                    </tr>
                    <tr>
                      <td>Transport Allowance</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$200</td>
                    </tr>
                    <tr>
                      <td>Overtime</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$150</td>
                    </tr>
                    <tr style={{ borderTop: '2px solid #dee2e6', fontWeight: 'bold' }}>
                      <td>Total Earnings</td>
                      <td style={{ textAlign: 'right', color: '#27ae60' }}>$5,150</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div>
                <h4>Deductions</h4>
                <table className="table">
                  <tbody>
                    <tr>
                      <td>Tax</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$200</td>
                    </tr>
                    <tr>
                      <td>Social Security</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$50</td>
                    </tr>
                    <tr>
                      <td>Health Insurance</td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>$100</td>
                    </tr>
                    <tr style={{ borderTop: '2px solid #dee2e6', fontWeight: 'bold' }}>
                      <td>Total Deductions</td>
                      <td style={{ textAlign: 'right', color: '#e74c3c' }}>$350</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div style={{ borderTop: '3px solid #3498db', paddingTop: '1rem', marginTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>Net Pay</h3>
                <h3 style={{ color: '#3498db', fontSize: '2rem' }}>$4,800</h3>
              </div>
            </div>
          </div>
        </div>
        
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div className="card-header">Payslip History</div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Gross Pay</th>
                  <th>Deductions</th>
                  <th>Net Pay</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>November 2025</td>
                  <td>$5,150</td>
                  <td>$350</td>
                  <td>$4,800</td>
                  <td><button className="btn btn-secondary">Download</button></td>
                </tr>
                <tr>
                  <td>October 2025</td>
                  <td>$5,000</td>
                  <td>$300</td>
                  <td>$4,700</td>
                  <td><button className="btn btn-secondary">Download</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Payslip;