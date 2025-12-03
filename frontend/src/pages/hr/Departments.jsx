import React from 'react';

const Departments = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Department Management</h1>
        <button className="btn btn-primary">Add Department</button>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">All Departments</div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
              <div className="card">
                <div className="card-body">
                  <h3>Engineering</h3>
                  <p>Software development and technical operations</p>
                  <div><strong>Employees:</strong> 15</div>
                  <div><strong>Manager:</strong> Jane Smith</div>
                </div>
              </div>
              <div className="card">
                <div className="card-body">
                  <h3>Human Resources</h3>
                  <p>Employee management and organizational development</p>
                  <div><strong>Employees:</strong> 3</div>
                  <div><strong>Manager:</strong> Sarah Johnson</div>
                </div>
              </div>
              <div className="card">
                <div className="card-body">
                  <h3>Marketing</h3>
                  <p>Brand promotion and customer engagement</p>
                  <div><strong>Employees:</strong> 8</div>
                  <div><strong>Manager:</strong> Mike Wilson</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Departments;