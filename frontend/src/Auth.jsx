import React, { useState, createContext, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
      setLoading(true);
      // In production, this would be a real API call
      setTimeout(() => {
        try {
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
        } catch (err) {
          console.error('Login error:', err);
          reject(err);
        } finally {
          setLoading(false);
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
    return new Promise((resolve, reject) => {
      setLoading(true);
      // Mock registration
      setTimeout(() => {
        try {
          // Basic validation
          if (!email.includes('@') || password.length < 6) {
            reject(new Error('Invalid email or password (min 6 characters)'));
            return;
          }
          
          const token = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
          localStorage.setItem('auth_token', token);
          
          const userData = {
            id: Math.random().toString(36).substring(2),
            name,
            email
          };
          
          setUser(userData);
          setIsAuthenticated(true);
          resolve(userData);
        } catch (err) {
          console.error('Registration error:', err);
          reject(err);
        } finally {
          setLoading(false);
        }
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, register } = useAuth();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      if (isRegister) {
        if (!name) {
          setError(t('auth.nameRequired'));
          setIsSubmitting(false);
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
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-form-container">
      <h2>{isRegister ? t('auth.register') : t('auth.login')}</h2>
      
      {error && <div className="auth-error" role="alert">{error}</div>}
      
      <form onSubmit={handleSubmit} className="auth-form" aria-labelledby="auth-form-title">
        <div id="auth-form-title" className="visually-hidden">
          {isRegister ? t('auth.register') : t('auth.login')} {t('auth.formTitle')}
        </div>
        
        {isRegister && (
          <div className="form-group">
            <label htmlFor="name">{t('auth.name')}</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('auth.name')}
              required
              aria-required="true"
              disabled={isSubmitting}
            />
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="email">{t('auth.email')}</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email@example.com"
            required
            aria-required="true"
            disabled={isSubmitting}
            autoComplete="username"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">{t('auth.password')}</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="********"
            required
            aria-required="true"
            disabled={isSubmitting}
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            minLength={6}
          />
        </div>
        
        <button 
          type="submit" 
          className="auth-button"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isRegister ? t('auth.register') : t('auth.login')}
        </button>
      </form>
      
      <p className="auth-switch">
        {isRegister ? t('auth.loginToggle') : t('auth.registerToggle')}
        <button 
          className="auth-switch-button"
          onClick={() => setIsRegister(!isRegister)}
          type="button"
          disabled={isSubmitting}
        >
          {isRegister ? t('auth.login') : t('auth.register')}
        </button>
      </p>
      
      <div className="auth-demo-info">
        <p>{t('auth.demoCredentials')}</p>
        <p>{t('auth.demoEmail')}</p>
        <p>{t('auth.demoPassword')}</p>
      </div>
    </div>
  );
};

export { LoginForm };
