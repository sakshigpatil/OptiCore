import React from 'react';
import './AuthLayout.css';

const AuthLayout = ({ children }) => {
  return (
    <div className="auth-layout">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-logo">HRMS</h1>
          <p className="auth-subtitle">Human Resource Management System</p>
        </div>
        <div className="auth-content">
          {children}
        </div>
        <div className="auth-footer">
          <p>&copy; 2025 HRMS. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;