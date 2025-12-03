import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: '#f8f9fa'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '500px', padding: '2rem' }}>
        <div style={{ fontSize: '6rem', fontWeight: 'bold', color: '#e74c3c', marginBottom: '1rem' }}>
          404
        </div>
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#2c3e50' }}>
          Page Not Found
        </h1>
        <p style={{ color: '#7f8c8d', marginBottom: '2rem', fontSize: '1.1rem' }}>
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to="/" className="btn btn-primary" style={{ textDecoration: 'none' }}>
          Go Back Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;