import React from 'react';
import { useSelector } from 'react-redux';
import LogoutButton from '../auth/LogoutButton';

const Header = () => {
  const { user } = useSelector((state) => state.auth);

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo">HRMS</h1>
        </div>
        <div className="header-right">
          {user && (
            <div className="user-menu">
              <span className="user-name">
                Welcome, {user.role === 'ADMIN_HR' ? 'HR Administrator' : 
                         user.role === 'MANAGER' ? 'Department Manager' : 
                         user.first_name + ' ' + user.last_name}
              </span>
              <LogoutButton className="logout-btn">
                Logout
              </LogoutButton>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;