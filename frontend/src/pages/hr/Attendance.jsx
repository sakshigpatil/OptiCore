import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';

const Attendance = () => {
  const [attendanceData, setAttendanceData] = useState([]);
  const [summary, setSummary] = useState({
    present: 0,
    absent: 0,
    late: 0,
    totalEmployees: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTodaysAttendance();
  }, []);

  const fetchTodaysAttendance = async () => {
    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      
      // Fetch today's attendance records
      const attendanceResponse = await api.get(`/attendance/?date=${today}`);
      const records = attendanceResponse.results || attendanceResponse || [];
      
      // Fetch all employees to calculate absent count
      const employeesResponse = await api.get('/employees/');
      const allEmployees = employeesResponse.results || employeesResponse || [];
      
      // Calculate summary statistics
      const presentCount = records.filter(record => 
        ['PRESENT', 'LATE', 'OVERTIME'].includes(record.status)
      ).length;
      
      const lateCount = records.filter(record => 
        record.status === 'LATE'
      ).length;
      
      const totalEmployees = allEmployees.length;
      const absentCount = totalEmployees - records.length;
      
      setSummary({
        present: presentCount,
        absent: absentCount,
        late: lateCount,
        totalEmployees: totalEmployees
      });
      
      setAttendanceData(records);
      
    } catch (error) {
      console.error('Error fetching attendance data:', error);
      toast.error('Failed to fetch attendance data');
      // Set fallback data
      setAttendanceData([]);
      setSummary({ present: 0, absent: 0, late: 0, totalEmployees: 0 });
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateTimeString) => {
    if (!dateTimeString) return '-';
    try {
      const date = new Date(dateTimeString);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch (error) {
      return '-';
    }
  };

  const formatHours = (hours) => {
    if (!hours) return '-';
    return `${parseFloat(hours).toFixed(2)} hours`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PRESENT':
      case 'OVERTIME':
        return '#27ae60';
      case 'LATE':
        return '#f39c12';
      case 'ABSENT':
        return '#e74c3c';
      case 'HALF_DAY':
        return '#3498db';
      default:
        return '#95a5a6';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'PRESENT':
        return 'Present';
      case 'LATE':
        return 'Late';
      case 'ABSENT':
        return 'Absent';
      case 'OVERTIME':
        return 'Overtime';
      case 'HALF_DAY':
        return 'Half Day';
      case 'EARLY_OUT':
        return 'Early Out';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">Attendance Management</h1>
        </div>
        <div className="page-content">
          <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading attendance data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Attendance Management</h1>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span>Today's Attendance</span>
            <button className="btn btn-primary btn-sm" onClick={fetchTodaysAttendance}>
              <i className="fas fa-sync-alt me-1"></i> Refresh
            </button>
          </div>
          <div className="card-body">
            {/* Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div className="card">
                <div className="card-body text-center">
                  <h3 style={{ color: '#27ae60', margin: '0 0 10px 0' }}>Present</h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#27ae60' }}>
                    {summary.present}
                  </div>
                  <small className="text-muted">out of {summary.totalEmployees}</small>
                </div>
              </div>
              <div className="card">
                <div className="card-body text-center">
                  <h3 style={{ color: '#e74c3c', margin: '0 0 10px 0' }}>Absent</h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#e74c3c' }}>
                    {summary.absent}
                  </div>
                  <small className="text-muted">employees</small>
                </div>
              </div>
              <div className="card">
                <div className="card-body text-center">
                  <h3 style={{ color: '#f39c12', margin: '0 0 10px 0' }}>Late</h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f39c12' }}>
                    {summary.late}
                  </div>
                  <small className="text-muted">arrivals</small>
                </div>
              </div>
            </div>

            {/* Attendance Table */}
            {attendanceData.length === 0 ? (
              <div className="text-center py-4">
                <i className="fas fa-calendar-times fa-3x text-muted mb-3"></i>
                <h5 className="text-muted">No Attendance Records</h5>
                <p className="text-muted">No attendance data found for today.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead className="table-header">
                    <tr>
                      <th>Employee</th>
                      <th>Check In</th>
                      <th>Check Out</th>
                      <th>Working Hours</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceData.map((record) => (
                      <tr key={record.id}>
                        <td>
                          <div>
                            <strong>
                              {record.employee?.user?.first_name} {record.employee?.user?.last_name}
                            </strong>
                            <br />
                            <small className="text-muted">{record.employee?.employee_id}</small>
                          </div>
                        </td>
                        <td>{formatTime(record.clock_in_time)}</td>
                        <td>{formatTime(record.clock_out_time)}</td>
                        <td>{formatHours(record.total_hours)}</td>
                        <td>
                          <span 
                            style={{ 
                              color: getStatusColor(record.status), 
                              fontWeight: 'bold' 
                            }}
                          >
                            {getStatusLabel(record.status)}
                          </span>
                          {record.is_overtime && (
                            <small className="d-block text-warning">
                              OT: {formatHours(record.overtime_hours)}
                            </small>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Attendance;