import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  ChartBarIcon,
  UsersIcon,
  CheckCircleIcon,
  BuildingOfficeIcon,
  CalendarIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  UserIcon,
  ClipboardDocumentListIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';
import '../../styles/enhanced-sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useSelector((state) => state.auth);

  // Get menu items based on user role
  const getMenuItems = () => {
    if (user?.role === 'ADMIN_HR') {
      return [
        { path: '/hr/dashboard', label: 'HR Dashboard', icon: ChartBarIcon },
        { path: '/hr/employees', label: 'Employees', icon: UsersIcon },
        { path: '/hr/employee-approvals', label: 'Employee Approvals', icon: CheckCircleIcon },
        { path: '/hr/departments', label: 'Departments', icon: BuildingOfficeIcon },
        { path: '/hr/attendance', label: 'Attendance', icon: CalendarIcon },
        { path: '/hr/leaves', label: 'Leave Requests', icon: DocumentTextIcon },
        { path: '/hr/payroll', label: 'Payroll', icon: CurrencyDollarIcon },
        { path: '/hr/performance', label: 'Performance', icon: BeakerIcon },
        { path: '/hr/scheduled-reports', label: 'Scheduled Reports', icon: ClipboardDocumentListIcon },
        { path: '/hr/custom-reports', label: 'Custom Reports', icon: DocumentTextIcon },
      ];
    } else if (user?.role === 'MANAGER') {
      return [
        { path: '/manager/dashboard', label: 'Manager Dashboard', icon: ChartBarIcon },
        { path: '/manager/performance', label: 'Performance', icon: BeakerIcon },
        { path: '/manager/employees', label: 'My Team', icon: UsersIcon },
        { path: '/manager/leaves', label: 'Leave Approvals', icon: CheckCircleIcon },
        { path: '/manager/attendance', label: 'Team Attendance', icon: CalendarIcon },
        { path: '/manager/employee-approvals', label: 'Employee Requests', icon: DocumentTextIcon },
      ];
    } else {
      return [
        { path: '/employee/dashboard', label: 'Dashboard', icon: ChartBarIcon },
        { path: '/employee/performance', label: 'Performance', icon: BeakerIcon },
        { path: '/employee/profile', label: 'Profile', icon: UserIcon },
        { path: '/employee/tasks', label: 'Tasks', icon: ClipboardDocumentListIcon },
        { path: '/employee/attendance', label: 'My Attendance', icon: CalendarIcon },
        { path: '/employee/leaves', label: 'My Leaves', icon: DocumentTextIcon },
        { path: '/employee/payslip', label: 'Payslip', icon: CurrencyDollarIcon },
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
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <li key={item.path} className={`nav-item ${isActive(item.path) ? 'active' : ''}`}>
                <Link to={item.path} className="nav-link">
                  <span className="nav-icon">
                    <IconComponent className="w-5 h-5" />
                  </span>
                  <span className="nav-label">{item.label}</span>
                </Link>
              </li>
            );
          })}
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