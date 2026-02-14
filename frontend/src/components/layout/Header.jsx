import React from 'react';
import { useSelector } from 'react-redux';
import { BellIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import LogoutButton from '../auth/LogoutButton';

const Header = () => {
  const { user } = useSelector((state) => state.auth);

  const getInitials = (firstName, lastName) => {
    return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
  };

  const getRoleDisplay = (role) => {
    switch(role) {
      case 'ADMIN_HR': return 'HR Administrator';
      case 'MANAGER': return 'Department Manager';
      default: return 'Employee';
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo">HRMS</h1>
        </div>
        <div className="header-right">
          {user && (
            <>
              {/* Notification Bell */}
              <button className="notification-btn">
                <BellIcon className="h-6 w-6" />
                <span className="notification-badge">3</span>
              </button>

              {/* Settings */}
              <button className="settings-btn">
                <Cog6ToothIcon className="h-6 w-6" />
              </button>

              {/* User Profile Section */}
              <div className="user-profile-section">
                <div className="user-avatar-circle">
                  {getInitials(user.first_name, user.last_name)}
                </div>
                <div className="user-info-header">
                  <div className="user-name-header">
                    {user.first_name} {user.last_name}
                  </div>
                  <div className="user-role-header">
                    {getRoleDisplay(user.role)}
                  </div>
                </div>
              </div>

              <LogoutButton className="logout-btn-header">
                Logout
              </LogoutButton>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;