import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import '../../styles/enhanced-sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useSelector((state) => state.auth);

  // Get menu items based on user role
  const getMenuItems = () => {
    if (user?.role === 'ADMIN_HR') {
      return [
        { path: '/hr/dashboard', label: 'HR Dashboard', icon: '📊' },
        { path: '/hr/employees', label: 'Employees', icon: '👥' },
        { path: '/hr/employee-approvals', label: 'Employee Approvals', icon: '✅' },
        { path: '/hr/departments', label: 'Departments', icon: '🏢' },
        { path: '/hr/attendance', label: 'Attendance', icon: '📅' },
        { path: '/hr/leaves', label: 'Leave Requests', icon: '🏖️' },
        { path: '/hr/payroll', label: 'Payroll', icon: '💰' },
      ];
    } else if (user?.role === 'MANAGER') {
      return [
        { path: '/manager/dashboard', label: 'Manager Dashboard', icon: '📊' },
        { path: '/manager/employees', label: 'My Team', icon: '👥' },
        { path: '/manager/leaves', label: 'Leave Approvals', icon: '✅' },
        { path: '/manager/attendance', label: 'Team Attendance', icon: '📅' },
        { path: '/manager/employee-approvals', label: 'Employee Requests', icon: '🏖️' },
      ];
    } else {
      return [
        { path: '/employee/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/employee/profile', label: 'Profile', icon: '👤' },
        { path: '/employee/tasks', label: 'Tasks', icon: '📋' },
        { path: '/employee/attendance', label: 'My Attendance', icon: '📅' },
        { path: '/employee/leaves', label: 'My Leaves', icon: '🏖️' },
        { path: '/employee/payslip', label: 'Payslip', icon: '💰' },
      ];
    }
  };

  const menuItems = getMenuItems();

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <ul className="nav-menu">
          {menuItems.map((item) => (
            <li key={item.path} className={`nav-item ${isActive(item.path) ? 'active' : ''}`}>
              <Link to={item.path} className="nav-link">
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      {user && (
        <div className="user-info">
          <div className="user-avatar">
            {user.first_name.charAt(0)}{user.last_name.charAt(0)}
          </div>
          <div className="user-details">
            <div className="user-name">{user.first_name} {user.last_name}</div>
            <div className="user-role">
              {user.role === 'ADMIN_HR' ? 'HR Administrator' : 
               user.role === 'MANAGER' ? 'Department Manager' : 
               user.role || 'Employee'}
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;