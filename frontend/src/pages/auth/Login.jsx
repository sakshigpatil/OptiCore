import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../../store/slices/authSlice';
import toast from 'react-hot-toast';
import './Login.css';
import './LoginIllustration.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [rememberMe, setRememberMe] = useState(false);
  
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
    <div className="modern-login-container">
      {/* Left Side - Login Form */}
      <div className="login-form-section">
        <div className="login-form-wrapper">
          <div className="login-header">
            <div className="logo-container">
              <div className="logo-icon">
                <div className="logo-squares">
                  <div className="square square-1"></div>
                  <div className="square square-2"></div>
                  <div className="square square-3"></div>
                </div>
                <div className="logo-glow"></div>
              </div>
              <div className="brand-text">
                <h2 className="brand-name">HRMS</h2>
                <span className="brand-tagline">Human Resources</span>
              </div>
            </div>
            <h1 className="welcome-title">Welcome Back!</h1>
            <p className="welcome-subtitle">Sign in to access your workspace</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <div className="input-wrapper">
                <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" strokeWidth="2"/>
                  <polyline points="22,6 12,13 2,6" stroke="currentColor" strokeWidth="2"/>
                </svg>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`form-input ${errors.email ? 'error' : ''}`}
                  placeholder="Enter your email address"
                />
              </div>
              {errors.email && <div className="error-message">{errors.email}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="input-wrapper">
                <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" strokeWidth="2"/>
                  <circle cx="12" cy="16" r="1" fill="currentColor"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" strokeWidth="2"/>
                </svg>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`form-input ${errors.password ? 'error' : ''}`}
                  placeholder="Enter your password"
                />
              </div>
              {errors.password && <div className="error-message">{errors.password}</div>}
            </div>

            <div className="form-options">
              <label className="checkbox-container">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span className="checkmark"></span>
                Remember me
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Forgot Password?
              </Link>
            </div>

            <button 
              type="submit" 
              className="login-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="loading-spinner"></div>
                  Signing In...
                </>
              ) : (
                <>
                  Login
                  <svg className="login-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12h14m-7-7l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </>
              )}
            </button>
          </form>

          <div className="login-footer">
            <p className="signup-text">
              By creating an account, you agree to our{' '}
              <Link to="/terms" className="terms-link">Terms of Service</Link>{' '}
              and{' '}
              <Link to="/privacy" className="terms-link">Privacy Policy</Link>
            </p>
            <p className="signup-link">
              Don't have an account?{' '}
              <Link to="/register" className="signup-button">Sign Up</Link>
            </p>
          </div>
        </div>
      </div>

      {/* Right Side - Illustration */}
      <div className="login-illustration-section">
        <div className="bg-pattern"></div>
        <div className="illustration-content">
          <div className="illustration-card">
            <div className="card-glow"></div>
            <div className="illustration-scene">
              {/* Background elements */}
              <div className="bg-circles">
                <div className="circle circle-1"></div>
                <div className="circle circle-2"></div>
                <div className="circle circle-3"></div>
              </div>
              
              {/* Main illustration */}
              <div className="main-illustration">
                {/* Workspace setup */}
                <div className="workspace">
                  <div className="desk-surface"></div>
                  <div className="monitor">
                    <div className="monitor-screen">
                      <div className="screen-content">
                        <div className="chart-bar bar-1"></div>
                        <div className="chart-bar bar-2"></div>
                        <div className="chart-bar bar-3"></div>
                      </div>
                    </div>
                    <div className="monitor-stand"></div>
                  </div>
                  
                  {/* Person */}
                  <div className="person">
                    <div className="person-head">
                      <div className="hair"></div>
                      <div className="face"></div>
                    </div>
                    <div className="person-body"></div>
                    <div className="arms">
                      <div className="arm-left"></div>
                      <div className="arm-right"></div>
                    </div>
                  </div>
                  
                  {/* Chair */}
                  <div className="office-chair">
                    <div className="chair-back"></div>
                    <div className="chair-seat"></div>
                    <div className="chair-base"></div>
                  </div>
                </div>
                
                {/* Floating UI elements */}
                <div className="ui-elements">
                  <div className="ui-card ui-card-1">
                    <div className="card-header"></div>
                    <div className="card-content">
                      <div className="content-line"></div>
                      <div className="content-line short"></div>
                    </div>
                  </div>
                  <div className="ui-card ui-card-2">
                    <div className="notification-dot"></div>
                    <div className="notification-text"></div>
                  </div>
                  <div className="progress-ring">
                    <svg className="progress-svg" width="40" height="40">
                      <circle cx="20" cy="20" r="15" className="progress-bg"/>
                      <circle cx="20" cy="20" r="15" className="progress-fill"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="illustration-text">
              <h2>Modern Workspace</h2>
              <p>Experience the future of human resource management with our intuitive platform</p>
            </div>
            
            <div className="feature-highlights">
              <div className="feature-item">
                <div className="feature-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <span>Easy to Use</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <rect x="2" y="6" width="20" height="12" rx="2" stroke="currentColor" strokeWidth="2"/>
                    <circle cx="8" cy="12" r="2" stroke="currentColor" strokeWidth="2"/>
                    <path d="M16 12h4" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <span>Secure & Fast</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2"/>
                    <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" strokeWidth="2"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <span>Team Focused</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;