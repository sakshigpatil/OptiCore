import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../../store/slices/authSlice';
import toast from 'react-hot-toast';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading } = useSelector((state) => state.auth);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      console.log('Attempting login with:', { email: formData.email })
      const result = await dispatch(login(formData)).unwrap();
      console.log('Login successful:', result)
      toast.success('Login successful!');
      navigate('/');
    } catch (error) {
      console.error('Login failed:', error)
      toast.error(error || 'Login failed');
    }
  };

  return (
    <div className="auth-form">
      <h2 style={{ marginBottom: '1.5rem', textAlign: 'center', color: '#333' }}>Sign In</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="auth-form-group">
          <label className="auth-form-label">Email Address</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`auth-form-control ${errors.email ? 'error' : ''}`}
            placeholder="Enter your email"
          />
          {errors.email && <div className="auth-error">{errors.email}</div>}
        </div>

        <div className="auth-form-group">
          <label className="auth-form-label">Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className={`auth-form-control ${errors.password ? 'error' : ''}`}
            placeholder="Enter your password"
          />
          {errors.password && <div className="auth-error">{errors.password}</div>}
        </div>

        <button 
          type="submit" 
          className="auth-btn"
          disabled={loading}
        >
          {loading && <div className="auth-loading"></div>}
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>

      <Link to="/register" className="auth-link">
        Don't have an account? Sign up here
      </Link>
    </div>
  );
};

export default Login;