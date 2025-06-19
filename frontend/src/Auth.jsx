import React, { useState, createContext, useContext, useEffect } from 'react';
import './auth.css';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock authentication - in production, replace with real authentication
  useEffect(() => {
    // Check local storage for existing auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Mock user data
      setUser({
        id: '1',
        name: 'Demo User',
        email: 'user@example.com'
      });
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const login = (email, password) => {
    return new Promise((resolve, reject) => {
      // In production, this would be a real API call
      setTimeout(() => {
        if (email === 'user@example.com' && password === 'password') {
          const token = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
          localStorage.setItem('auth_token', token);
          
          const userData = {
            id: '1',
            name: 'Demo User',
            email
          };
          
          setUser(userData);
          setIsAuthenticated(true);
          resolve(userData);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 500);
    });
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const register = (name, email, password) => {
    return new Promise((resolve) => {
      // Mock registration
      setTimeout(() => {
        const token = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
        localStorage.setItem('auth_token', token);
        
        const userData = {
          id: '1',
          name,
          email
        };
        
        setUser(userData);
        setIsAuthenticated(true);
        resolve(userData);
      }, 500);
    });
  };

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
    register,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const LoginForm = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (isRegister) {
        if (!name) {
          setError('Name is required');
          return;
        }
        await register(name, email, password);
      } else {
        await login(email, password);
      }
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-form-container">
      <h2>{isRegister ? 'Create Account' : 'Login'}</h2>
      
      {error && <div className="auth-error">{error}</div>}
      
      <form onSubmit={handleSubmit} className="auth-form">
        {isRegister && (
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              required
            />
          </div>
        )}
        
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email@example.com"
            required
          />
        </div>
        
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="********"
            required
          />
        </div>
        
        <button type="submit" className="auth-button">
          {isRegister ? 'Register' : 'Login'}
        </button>
      </form>
      
      <p className="auth-switch">
        {isRegister ? 'Already have an account? ' : 'Need an account? '}
        <button 
          className="auth-switch-button"
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister ? 'Login' : 'Register'}
        </button>
      </p>
      
      <div className="auth-demo-info">
        <p>Demo credentials:</p>
        <p>Email: user@example.com</p>
        <p>Password: password</p>
      </div>
    </div>
  );
};

export { LoginForm };
