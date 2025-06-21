import React, { useState, createContext, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './auth.css';
import supabase from './supabaseClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const supa = supabase;

  // Supabase Auth session check
  useEffect(() => {
    const init = async () => {
      const { data: { session } } = await supa.auth.getSession();
      if (session) {
        const supaUser = session.user;
        setUser({ id: supaUser.id, name: supaUser.user_metadata?.name || supaUser.email, email: supaUser.email });
        setIsAuthenticated(true);
        // Fetch preferred language
        const { data: profile } = await supa.from('profiles').select('preferred_language').eq('id', supaUser.id).single();
        if (profile?.preferred_language) {
          import('./i18n').then(({ default: i18n }) => {
            i18n.changeLanguage(profile.preferred_language);
            localStorage.setItem('language', profile.preferred_language);
          });
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    const { data, error } = await supa.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (error) throw error;
    const u = data.user;
    setUser({ id: u.id, name: u.email, email: u.email });
    setIsAuthenticated(true);
    return u;
  };

  const logout = async () => {
    await supa.auth.signOut();
    setUser(null);
    setIsAuthenticated(false);
  };

  const register = async (name, email, password) => {
    setLoading(true);
    const { data, error } = await supa.auth.signUp({ email, password, options: { data: { name } } });
    setLoading(false);
    if (error) throw error;
    const u = data.user;
    // insert profile row
    await supa.from('profiles').upsert({ id: u.id, name, preferred_language: localStorage.getItem('language') || 'en' });
    setUser({ id: u.id, name, email });
    setIsAuthenticated(true);
    return u;
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
