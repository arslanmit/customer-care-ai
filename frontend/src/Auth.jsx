import React, { useState, createContext, useContext, useEffect } from 'react';
import './auth.css';
import supabase from './supabaseClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [role, setRole] = useState('user');
  const [loading, setLoading] = useState(true);

  const supa = supabase;
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Check existing JWT with backend /me
  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await fetch(`${API_BASE_URL}/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Invalid token');
        const me = await res.json();
        const supaUser = session.user;
        // Fetch profile including role
        const { data: profile } = await supa
          .from('profiles')
          .select('preferred_language, role, name')
          .eq('id', supaUser.id)
          .single();

        setUser({ id: supaUser.id, name: profile?.name || supaUser.user_metadata?.name || supaUser.email, email: supaUser.email });
        setRole(profile?.role || 'user');
        setIsAuthenticated(true);
        // Persist JWT for backend calls
        localStorage.setItem('auth_token', session.access_token);
        // No longer fetching language preferences as we're English-only
        setUser({ id: me.id, name: me.name || me.email, email: me.email });
        setRole(me.role || 'user');
        setIsAuthenticated(true);
        // language fetch from Supabase profile if supabase cred still valid
      } catch (e) {
        console.warn('Session init failed', e);
        localStorage.removeItem('auth_token');
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    setLoading(false);
    if (!res.ok) throw new Error('Invalid credentials');
    const { access_token } = await res.json();
    localStorage.setItem('auth_token', access_token);
    // fetch user details
    const meRes = await fetch(`${API_BASE_URL}/me`, { headers: { 'Authorization': `Bearer ${access_token}` } });
    const me = await meRes.json();
    setUser({ id: me.id, name: me.name || me.email, email: me.email });
    setRole(me.role || 'user');
    setIsAuthenticated(true);
    return me;
  };

  const logout = async () => {
    // No backend logout required for stateless JWT
    localStorage.removeItem('auth_token');
    setUser(null);
    setRole('user');
    setIsAuthenticated(false);

  };

  const register = async (name, email, password) => {
    setLoading(true);
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    setLoading(false);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    const { access_token } = await res.json();
    localStorage.setItem('auth_token', access_token);
    const meRes = await fetch(`${API_BASE_URL}/me`, { headers: { 'Authorization': `Bearer ${access_token}` } });
    const me = await meRes.json();
    // insert profile row
    setUser({ id: me.id, name: me.name || name, email: me.email });
    setRole(me.role || 'user');
    setIsAuthenticated(true);
    return me;
  };

  const value = {
    isAuthenticated,
    user,
    role,
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      if (isRegister) {
        if (!name) {
          setError('Name is required');
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
      <h2>{isRegister ? 'Register' : 'Login'}</h2>
      
      {error && <div className="auth-error" role="alert">{error}</div>}
      
      <form onSubmit={handleSubmit} className="auth-form" aria-labelledby="auth-form-title">
        <div id="auth-form-title" className="visually-hidden">
          {isRegister ? 'Register' : 'Login'} Form
        </div>
        
        {isRegister && (
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              required
              aria-required="true"
              disabled={isSubmitting}
            />
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
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
          <label htmlFor="password">Password</label>
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
        {isRegister ? 'Already have an account?' : 'Don\'t have an account?'}
        <button 
          className="auth-switch-button"
          onClick={() => setIsRegister(!isRegister)}
          type="button"
          disabled={isSubmitting}
        >
          {isRegister ? 'Login' : 'Register'}
        </button>
      </p>
      
      <div className="auth-demo-info">
        <p>Demo Credentials:</p>
        <p>Email: demo@example.com</p>
        <p>Password: password123</p>
      </div>
    </div>
  );
};

export { LoginForm };
