import React from 'react';
import { useSelector } from 'react-redux';

const UserDebug = () => {
  const { user, isLoading, isAuthenticated, token } = useSelector((state) => state.auth);

  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: '#f8f9fa',
      border: '1px solid #dee2e6',
      borderRadius: '5px',
      padding: '10px',
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
    }}>
      <strong>🐛 User Debug Info</strong>
      <div><strong>Is Authenticated:</strong> {String(isAuthenticated)}</div>
      <div><strong>Is Loading:</strong> {String(isLoading)}</div>
      <div><strong>Has Token:</strong> {token ? 'Yes' : 'No'}</div>
      <div><strong>User:</strong> {user ? JSON.stringify(user, null, 2) : 'null'}</div>
    </div>
  );
};

export default UserDebug;