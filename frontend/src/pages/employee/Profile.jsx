import React from 'react';

const Profile = () => {
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
                JD
              </div>
              <h3>John Doe</h3>
              <p style={{ color: '#7f8c8d' }}>Software Developer</p>
            </div>
          </div>
          <div className="card">
            <div className="card-header">Personal Information</div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label className="form-label">First Name</label>
                  <input type="text" className="form-control" value="John" readOnly />
                </div>
                <div>
                  <label className="form-label">Last Name</label>
                  <input type="text" className="form-control" value="Doe" readOnly />
                </div>
                <div>
                  <label className="form-label">Email</label>
                  <input type="email" className="form-control" value="john.doe@company.com" readOnly />
                </div>
                <div>
                  <label className="form-label">Phone</label>
                  <input type="text" className="form-control" value="+1 (555) 123-4567" readOnly />
                </div>
                <div>
                  <label className="form-label">Department</label>
                  <input type="text" className="form-control" value="Engineering" readOnly />
                </div>
                <div>
                  <label className="form-label">Position</label>
                  <input type="text" className="form-control" value="Software Developer" readOnly />
                </div>
                <div>
                  <label className="form-label">Employee ID</label>
                  <input type="text" className="form-control" value="EMP001" readOnly />
                </div>
                <div>
                  <label className="form-label">Join Date</label>
                  <input type="text" className="form-control" value="January 15, 2023" readOnly />
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