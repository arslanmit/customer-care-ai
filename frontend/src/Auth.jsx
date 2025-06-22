import React, { useState, createContext, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
        // Fetch preferred language separately to avoid variable shadowing
        const { data: langProfile } = await supa.from('profiles').select('preferred_language').eq('id', supaUser.id).single();
        if (langProfile?.preferred_language) {
          import('./i18n').then(({ default: i18n }) => {
            i18n.changeLanguage(langProfile.preferred_language);
            localStorage.setItem('language', langProfile.preferred_language);
          });
        }
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
