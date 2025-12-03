import React from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout, clearCredentials } from '../../store/slices/authSlice';
import { toast } from 'react-hot-toast';

const LogoutButton = ({ className = "logout-btn", children = "Logout" }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    // Show loading toast
    const loadingToast = toast.loading('Logging out...');
    
    // Clear credentials immediately (don't wait for API)
    dispatch(clearCredentials());
    
    // Dismiss loading toast and show success
    toast.dismiss(loadingToast);
    toast.success('Logged out successfully');
    
    // Navigate to login
    navigate('/login', { replace: true });
    
    // Optional: Try to call logout API in background (don't wait for it)
    const token = localStorage.getItem('refreshToken');
    if (token && token !== 'null') {
      dispatch(logout()).catch(() => {
        // Ignore API errors - user is already logged out locally
        console.log('Background logout API call failed, but user is already logged out locally');
      });
    }
  };

  return (
    <button onClick={handleLogout} className={className}>
      {children}
    </button>
  );
};

export default LogoutButton;