import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const Payslip = () => {
  const [payslips, setPayslips] = useState([]);
  const [currentPayslip, setCurrentPayslip] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);

  useEffect(() => {
    fetchPayslips();
  }, []);

  const fetchPayslips = async () => {
    setLoading(true);
    try {
      const response = await api.get('/payroll/payslips/');
      setPayslips(response.results || response.data || []);
    } catch (error) {
      console.error('Error fetching payslips:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPayslipByMonth = async (year, month) => {
    setLoading(true);
    try {
      const response = await api.get(`/payroll/payslips/?year=${year}&month=${month}`);
      const payslipData = response.results || response.data || [];
      if (payslipData.length > 0) {
        setCurrentPayslip(payslipData[0]);
      } else {
        setCurrentPayslip(null);
      }
    } catch (error) {
      console.error('Error fetching payslip:', error);
      setCurrentPayslip(null);
    } finally {
      setLoading(false);
    }
  };

  const handleViewPayslip = (payslip) => {
    setCurrentPayslip(payslip);
    setSelectedYear(payslip.payroll_run?.year || new Date().getFullYear());
    setSelectedMonth(payslip.payroll_run?.month || new Date().getMonth() + 1);
  };

  const handleSearchPayslip = () => {
    fetchPayslipByMonth(selectedYear, selectedMonth);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatMonth = (month, year) => {
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const renderPayslipDetails = () => {
    if (!currentPayslip) {
      return (
        <div className="card" style={{ marginTop: '1rem' }}>
          <div className="card-body" style={{ textAlign: 'center', padding: '3rem' }}>
            <h5 style={{ color: '#666' }}>No payslip found</h5>
            <p>No payslip available for the selected month.</p>
          </div>
        </div>
      );
    }

    const components = currentPayslip.components || {};

    return (
      <div className="card" style={{ marginTop: '1rem' }}>
        <div className="card-header" style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
          <h4 style={{ margin: 0, color: '#495057' }}>
            💰 Payslip - {formatMonth(currentPayslip.payroll_run?.month, currentPayslip.payroll_run?.year)}
          </h4>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
            {/* Employee Info */}
            <div>
              <h6 style={{ borderBottom: '1px solid #dee2e6', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                Employee Information
              </h6>
              <p><strong>Name:</strong> {currentPayslip.employee_name}</p>
              <p><strong>Pay Period:</strong> {formatMonth(currentPayslip.payroll_run?.month, currentPayslip.payroll_run?.year)}</p>
              <p><strong>Generated:</strong> {new Date(currentPayslip.generated_at).toLocaleDateString()}</p>
            </div>

            {/* Summary */}
            <div>
              <h6 style={{ borderBottom: '1px solid #dee2e6', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                Summary
              </h6>
              <div style={{ backgroundColor: '#e8f5e9', padding: '1rem', borderRadius: '4px' }}>
                <p style={{ margin: 0, fontSize: '1.1rem' }}>
                  <strong>Gross Salary:</strong> <span style={{ color: '#27ae60' }}>{formatCurrency(currentPayslip.gross_salary)}</span>
                </p>
                <p style={{ margin: '0.5rem 0', fontSize: '1.1rem' }}>
                  <strong>Total Deductions:</strong> <span style={{ color: '#e74c3c' }}>{formatCurrency(currentPayslip.total_deductions)}</span>
                </p>
                <hr style={{ margin: '0.5rem 0' }} />
                <p style={{ margin: 0, fontSize: '1.3rem', fontWeight: 'bold' }}>
                  <strong>Net Salary:</strong> <span style={{ color: '#2c3e50' }}>{formatCurrency(currentPayslip.net_salary)}</span>
                </p>
              </div>
            </div>
          </div>

          {/* Earnings & Deductions */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Earnings */}
            <div>
              <h6 style={{ borderBottom: '1px solid #dee2e6', paddingBottom: '0.5rem', marginBottom: '1rem', color: '#27ae60' }}>
                💰 Earnings
              </h6>
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Basic Salary</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.basic)}</td>
                  </tr>
                  <tr>
                    <td>HRA</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.hra)}</td>
                  </tr>
                  <tr>
                    <td>Conveyance</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.conveyance)}</td>
                  </tr>
                  <tr>
                    <td>Other Allowances</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.other_allowances)}</td>
                  </tr>
                  <tr style={{ borderTop: '2px solid #dee2e6', fontWeight: 'bold' }}>
                    <td>Total Earnings</td>
                    <td style={{ textAlign: 'right', color: '#27ae60' }}>{formatCurrency(components.gross)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Deductions */}
            <div>
              <h6 style={{ borderBottom: '1px solid #dee2e6', paddingBottom: '0.5rem', marginBottom: '1rem', color: '#e74c3c' }}>
                📉 Deductions
              </h6>
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td>Provident Fund (PF)</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.pf)}</td>
                  </tr>
                  <tr>
                    <td>Professional Tax</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.professional_tax)}</td>
                  </tr>
                  <tr>
                    <td>Income Tax</td>
                    <td style={{ textAlign: 'right' }}>{formatCurrency(components.tax)}</td>
                  </tr>
                  <tr style={{ borderTop: '2px solid #dee2e6', fontWeight: 'bold' }}>
                    <td>Total Deductions</td>
                    <td style={{ textAlign: 'right', color: '#e74c3c' }}>{formatCurrency(currentPayslip.total_deductions)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Download PDF Button */}
          {currentPayslip.payslip_pdf && (
            <div style={{ textAlign: 'center', marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #dee2e6' }}>
              <button 
                className="btn btn-primary"
                onClick={() => window.open(currentPayslip.payslip_pdf, '_blank')}
              >
                📄 Download PDF
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Payslips</h1>
      </div>
      
      <div className="page-content">
        {/* Search Controls */}
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div className="card-body">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Year</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  style={{ padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
                >
                  {[2024, 2025, 2026].map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Month</label>
                <select
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                  style={{ padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px' }}
                >
                  {Array.from({length: 12}, (_, i) => i + 1).map(month => (
                    <option key={month} value={month}>
                      {new Date(2025, month - 1).toLocaleDateString('en-US', { month: 'long' })}
                    </option>
                  ))}
                </select>
              </div>
              
              <div style={{ marginTop: '1.5rem' }}>
                <button 
                  className="btn btn-primary"
                  onClick={handleSearchPayslip}
                  disabled={loading}
                >
                  {loading ? 'Searching...' : 'View Payslip'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Payslips */}
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div className="card-header">
            <h5 style={{ margin: 0 }}>Recent Payslips</h5>
          </div>
          <div className="card-body">
            {payslips.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                No payslips available.
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Period</th>
                      <th>Gross Salary</th>
                      <th>Deductions</th>
                      <th>Net Salary</th>
                      <th>Generated</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payslips.map((payslip, index) => (
                      <tr key={index}>
                        <td>{formatMonth(payslip.payroll_run?.month, payslip.payroll_run?.year)}</td>
                        <td style={{ color: '#27ae60', fontWeight: 'bold' }}>{formatCurrency(payslip.gross_salary)}</td>
                        <td style={{ color: '#e74c3c' }}>{formatCurrency(payslip.total_deductions)}</td>
                        <td style={{ color: '#2c3e50', fontWeight: 'bold' }}>{formatCurrency(payslip.net_salary)}</td>
                        <td>{new Date(payslip.generated_at).toLocaleDateString()}</td>
                        <td>
                          <button 
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleViewPayslip(payslip)}
                          >
                            View Details
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

        {/* Payslip Details */}
        {renderPayslipDetails()}
      </div>
    </div>
  );
};

export default Payslip;