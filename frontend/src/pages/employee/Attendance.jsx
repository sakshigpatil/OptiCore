import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import api from '../../services/api';

const MyAttendance = () => {
  const [attendanceData, setAttendanceData] = useState({
    present_days: 20,
    absent_days: 2,
    total_hours: 176
  });
  const [recentAttendance, setRecentAttendance] = useState([
    {
      date: '2025-11-30',
      clock_in_time: '09:00 AM',
      clock_out_time: '06:00 PM',
      total_hours: '9 hours',
      status: 'Present'
    },
    {
      date: '2025-11-29', 
      clock_in_time: '09:15 AM',
      clock_out_time: '06:00 PM',
      total_hours: '8.75 hours',
      status: 'Late'
    }
  ]);
  const [currentStatus, setCurrentStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    fetchCurrentStatus();
    fetchAttendanceStats();
    fetchRecentAttendance();
  }, []);

  const fetchCurrentStatus = async () => {
    try {
      console.log('User object:', user);
      
      // Use the attendance API which should automatically get current user's data
      const response = await api.get('/attendance/current_status/');
      console.log('Current status response:', response);
      
      if (response.success) {
        console.log('Current status data:', response.data);
        console.log('Clock in time format:', response.data?.clock_in_time);
        console.log('Clock out time format:', response.data?.clock_out_time);
        console.log('Is clocked in (from API):', response.data?.is_clocked_in);
        
        // Check if the response indicates no attendance record for today
        if (response.data?.message === 'No attendance record for today') {
          setCurrentStatus({ is_clocked_in: false, message: 'No attendance record for today' });
        } else {
          setCurrentStatus(response.data || { is_clocked_in: false });
        }
      } else {
        console.log('No attendance data found');
        setCurrentStatus({ is_clocked_in: false });
      }
    } catch (error) {
      console.error('Error fetching current status:', error);
      console.error('Error details:', error.response?.data);
      setCurrentStatus({ is_clocked_in: false });
    }
  };

  const fetchAttendanceStats = async () => {
    try {
      const response = await api.get('/attendance/stats/');
      console.log('Stats response:', response);
      if (response.success && response.data) {
        setAttendanceData(response.data);
      }
    } catch (error) {
      console.error('Error fetching attendance stats:', error);
    }
  };

  const fetchRecentAttendance = async () => {
    try {
      const response = await api.get('/attendance/history/');
      console.log('History response:', response);
      console.log('Response.data type:', typeof response.data);
      console.log('Response.data:', response.data);
      
      // Handle both paginated and direct response formats
      let attendanceData = [];
      if (response.success && response.data) {
        attendanceData = response.data;
      } else if (response.results) {
        // Paginated response
        attendanceData = response.results;
      } else if (Array.isArray(response)) {
        // Direct array response
        attendanceData = response;
      }
      
      console.log('Setting recent attendance:', attendanceData.slice(0, 10));
      setRecentAttendance(attendanceData.slice(0, 10)); // Last 10 records
    } catch (error) {
      console.error('Error fetching recent attendance:', error);
    }
  };

  const handleClockInOut = async () => {
    setLoading(true);
    try {
      const isCurrentlyClockedIn = currentStatus?.clock_in_time && !currentStatus?.clock_out_time;
      
      if (isCurrentlyClockedIn) {
        // Clock Out
        console.log('Attempting to clock out...');
        const response = await api.post('/attendance/clock_out/', {});
        console.log('Clock out response:', response);
        console.log('Clock out response data:', response.data);
        
        if (response.data?.success || response.success) {
          alert('Successfully clocked out!');
          await fetchCurrentStatus();
          await fetchAttendanceStats();
          await fetchRecentAttendance();
        } else {
          alert(response.data?.message || response.message || 'Failed to clock out');
        }
      } else {
        // Clock In
        console.log('Attempting to clock in...');
        const response = await api.post('/attendance/clock_in/', {});
        console.log('Clock in response:', response);
        console.log('Clock in response data:', response.data);
        console.log('Full response object:', JSON.stringify(response, null, 2));
        
        if (response.data?.success || response.success) {
          alert('Successfully clocked in!');
          await fetchCurrentStatus();
          await fetchAttendanceStats();
          await fetchRecentAttendance();
        } else {
          alert(response.data?.message || response.message || 'Failed to clock in');
          console.error('Clock in failed:', response.data?.errors || response.errors);
        }
      }
    } catch (error) {
      console.error('Clock in/out error:', error);
      console.error('Full error:', error.response);
      alert(error.response?.data?.message || error.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getClockButtonText = () => {
    if (loading) return 'Processing...';
    if (!currentStatus) return 'Clock In';
    
    console.log('Current status for button:', currentStatus);
    console.log('Clock in time:', currentStatus.clock_in_time);
    console.log('Clock out time:', currentStatus.clock_out_time);
    
    // User is currently clocked in if they have clock in time but no clock out time
    const isCurrentlyClockedIn = currentStatus.clock_in_time && !currentStatus.clock_out_time;
    console.log('Is currently clocked in:', isCurrentlyClockedIn);
    
    return isCurrentlyClockedIn ? 'Clock Out' : 'Clock In';
  };

  const getClockButtonColor = () => {
    if (!currentStatus) return 'btn-success';
    const isCurrentlyClockedIn = currentStatus.clock_in_time && !currentStatus.clock_out_time;
    return isCurrentlyClockedIn ? 'btn-danger' : 'btn-success';
  };

  const formatTime = (timeString) => {
    if (!timeString) return null;
    
    try {
      // Handle different time formats
      let dateObj;
      
      if (timeString.includes('T')) {
        // ISO format: "2025-12-03T14:30:15.123456"
        dateObj = new Date(timeString);
      } else if (timeString.match(/^\d{2}:\d{2}:\d{2}/)) {
        // Time only format: "14:30:15"
        dateObj = new Date(`1970-01-01T${timeString}`);
      } else {
        // Try parsing as-is
        dateObj = new Date(timeString);
      }
      
      if (isNaN(dateObj.getTime())) {
        console.log('Invalid time format:', timeString);
        return timeString; // Return original if can't parse
      }
      
      return dateObj.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    } catch (error) {
      console.error('Error formatting time:', error, timeString);
      return timeString; // Return original string if error
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Attendance</h1>
        <button 
          className={`btn ${getClockButtonColor()}`}
          onClick={handleClockInOut}
          disabled={loading}
        >
          {getClockButtonText()}
        </button>
      </div>
      <div className="page-content">
        {/* Current Status Card */}
        {currentStatus && currentStatus.clock_in_time && (
          <div className="card" style={{ marginBottom: '2rem', backgroundColor: currentStatus.clock_out_time ? '#f8f9fa' : '#e8f5e8' }}>
            <div className="card-body">
              <h4 style={{ color: currentStatus.clock_out_time ? '#6c757d' : '#28a745' }}>
                {currentStatus.clock_out_time ? '✅ Work Day Completed' : '🕐 Currently Working'}
              </h4>
              <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '1rem' }}>
                DEBUG: clock_in_time={currentStatus.clock_in_time}, clock_out_time={currentStatus.clock_out_time}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                <div>
                  <strong>Clock In:</strong> {formatTime(currentStatus.clock_in_time) || 'Not clocked in'}
                </div>
                <div>
                  <strong>Clock Out:</strong> {formatTime(currentStatus.clock_out_time) || 'Not clocked out'}
                </div>
                <div>
                  <strong>Hours Worked:</strong> {currentStatus.total_hours || 'Calculating...'} hours
                </div>
                <div>
                  <strong>Status:</strong> <span style={{ 
                    color: currentStatus.status === 'PRESENT' ? '#28a745' : 
                          currentStatus.status === 'LATE' ? '#ffc107' : '#dc3545',
                    fontWeight: 'bold' 
                  }}>{currentStatus.status || 'In Progress'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#27ae60' }}>Present Days</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{attendanceData.present_days || 0}</div>
              <small style={{ color: '#7f8c8d' }}>This month</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#e74c3c' }}>Absent Days</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{attendanceData.absent_days || 0}</div>
              <small style={{ color: '#7f8c8d' }}>This month</small>
            </div>
          </div>
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#3498db' }}>Total Hours</h3>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{attendanceData.total_hours || 0}</div>
              <small style={{ color: '#7f8c8d' }}>This month</small>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            Recent Attendance
            <button 
              className="btn btn-secondary" 
              style={{ fontSize: '0.9rem', float: 'right' }}
              onClick={() => {
                fetchCurrentStatus();
                fetchAttendanceStats();
                fetchRecentAttendance();
              }}
            >
              🔄 Refresh
            </button>
          </div>
          <div className="card-body">
            {recentAttendance.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                No attendance records found.
              </div>
            ) : (
              <div className="table-responsive">
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
                    {recentAttendance.map((record, index) => (
                      <tr key={index}>
                        <td>{new Date(record.date).toLocaleDateString()}</td>
                        <td>{formatTime(record.clock_in_time) || '-'}</td>
                        <td>{formatTime(record.clock_out_time) || 'Not clocked out'}</td>
                        <td>{record.total_hours ? `${record.total_hours} hours` : '-'}</td>
                        <td>
                          <span style={{ 
                            color: record.status === 'PRESENT' ? '#27ae60' : 
                                  record.status === 'LATE' ? '#f39c12' : 
                                  record.status === 'ABSENT' ? '#e74c3c' : '#6c757d',
                            fontWeight: 'bold' 
                          }}>
                            {record.status || 'In Progress'}
                          </span>
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

export default MyAttendance;