import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import api from '../../services/api';

const Profile = () => {
  const { user } = useSelector((state) => state.auth);
  const [employeeData, setEmployeeData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEmployeeData = async () => {
      try {
        // Fetch employee data from API
        const response = await api.get(`/employees/my_profile/`);
        setEmployeeData(response);
      } catch (error) {
        console.error('Error fetching employee data:', error);
        // If API fails, use user data from auth
        setEmployeeData(null);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchEmployeeData();
    }
  }, [user]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading...</span>
        </div>
        <p style={{ marginTop: '1rem' }}>Loading profile...</p>
      </div>
    );
  }

  // Use employee data if available, otherwise fallback to user data
  const userInfo = employeeData?.user_details || user;
  const profileData = employeeData || {};
  const initials = userInfo ? `${userInfo.first_name?.[0] || ''}${userInfo.last_name?.[0] || ''}` : 'U';

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <button className="btn btn-primary">Edit Profile</button>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
          <div className="card">
            <div className="card-header">Profile Picture</div>
            <div className="card-body" style={{ textAlign: 'center' }}>
              <div style={{ 
                width: '120px', 
                height: '120px', 
                borderRadius: '50%', 
                background: '#3498db', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                fontSize: '3rem', 
                color: 'white', 
                fontWeight: 'bold', 
                margin: '0 auto 1rem' 
              }}>
                {initials}
              </div>
              <h3>{userInfo?.full_name || `${userInfo?.first_name || ''} ${userInfo?.last_name || ''}`}</h3>
              <p style={{ color: '#7f8c8d' }}>
                {profileData?.position || userInfo?.role?.replace('_', ' ') || 'Employee'}
              </p>
            </div>
          </div>
          <div className="card">
            <div className="card-header">Personal Information</div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label className="form-label">First Name</label>
                  <input type="text" className="form-control" value={userInfo?.first_name || ''} readOnly />
                </div>
                <div>
                  <label className="form-label">Last Name</label>
                  <input type="text" className="form-control" value={userInfo?.last_name || ''} readOnly />
                </div>
                <div>
                  <label className="form-label">Email</label>
                  <input type="email" className="form-control" value={userInfo?.email || ''} readOnly />
                </div>
                <div>
                  <label className="form-label">Phone</label>
                  <input type="text" className="form-control" value={userInfo?.phone || 'Not provided'} readOnly />
                </div>
                <div>
                  <label className="form-label">Department</label>
                  <input type="text" className="form-control" value={profileData?.department_name || 'Not assigned'} readOnly />
                </div>
                <div>
                  <label className="form-label">Position</label>
                  <input type="text" className="form-control" value={profileData?.position || 'Employee'} readOnly />
                </div>
                <div>
                  <label className="form-label">Employee ID</label>
                  <input type="text" className="form-control" value={profileData?.employee_id || 'N/A'} readOnly />
                </div>
                <div>
                  <label className="form-label">Hire Date</label>
                  <input type="text" className="form-control" value={
                    profileData?.hire_date 
                      ? new Date(profileData.hire_date).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })
                      : 'Not available'
                  } readOnly />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;