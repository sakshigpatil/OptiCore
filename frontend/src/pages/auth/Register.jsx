import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../../store/slices/authSlice';
import toast from 'react-hot-toast';

const Register = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'EMPLOYEE'
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
    
    if (!formData.first_name) {
      newErrors.first_name = 'First name is required';
    }
    
    if (!formData.last_name) {
      newErrors.last_name = 'Last name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!formData.username) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password_confirm) {
      newErrors.password_confirm = 'Please confirm your password';
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
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
      await dispatch(register(formData)).unwrap();
      toast.success('Registration successful! Your account is pending approval. You will be able to login once HR approves your account.');
      navigate('/login');
    } catch (error) {
      toast.error(error.message || 'Registration failed');
    }
  };

  return (
    <div className="auth-form">
      <h2 style={{ marginBottom: '1.5rem', textAlign: 'center', color: '#333' }}>Create Account</h2>
      
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="auth-form-group" style={{ flex: 1 }}>
            <label className="auth-form-label">First Name</label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className={`auth-form-control ${errors.first_name ? 'error' : ''}`}
              placeholder="First name"
            />
            {errors.first_name && <div className="auth-error">{errors.first_name}</div>}
          </div>

          <div className="auth-form-group" style={{ flex: 1 }}>
            <label className="auth-form-label">Last Name</label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className={`auth-form-control ${errors.last_name ? 'error' : ''}`}
              placeholder="Last name"
            />
            {errors.last_name && <div className="auth-error">{errors.last_name}</div>}
          </div>
        </div>

        <div className="auth-form-group">
          <label className="auth-form-label">Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className={`auth-form-control ${errors.username ? 'error' : ''}`}
            placeholder="Choose a username"
          />
          {errors.username && <div className="auth-error">{errors.username}</div>}
        </div>

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
            placeholder="Create a password"
          />
          {errors.password && <div className="auth-error">{errors.password}</div>}
        </div>

        <div className="auth-form-group">
          <label className="auth-form-label">Confirm Password</label>
          <input
            type="password"
            name="password_confirm"
            value={formData.password_confirm}
            onChange={handleChange}
            className={`auth-form-control ${errors.password_confirm ? 'error' : ''}`}
            placeholder="Confirm your password"
          />
          {errors.password_confirm && <div className="auth-error">{errors.password_confirm}</div>}
        </div>

        <button 
          type="submit" 
          className="auth-btn"
          disabled={loading}
        >
          {loading && <div className="auth-loading"></div>}
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>

      <Link to="/login" className="auth-link">
        Already have an account? Sign in here
      </Link>
    </div>
  );
};

export default Register;