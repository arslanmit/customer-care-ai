import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import './chatbot.css';
import Analytics from './Analytics';
import { useAuth, LoginForm, AuthProvider } from './Auth';
import './i18n';
import { logEvent } from './analyticsService';
import Feedback from './Feedback';
import supabase from './supabaseClient';

const RASA_BASE_URL = import.meta.env.VITE_RASA_URL || "http://localhost:5005";

const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();
  const { isAuthenticated, user } = useAuth();

  const languages = ['en', 'es', 'fr', 'de', 'tr'];

  return (
    <div className="language-switcher">
      <select 
        value={i18n.language} 
        onChange={(e) => {
          const lng = e.target.value;
          i18n.changeLanguage(lng);
          localStorage.setItem('language', lng);
          if (isAuthenticated && supabase && user?.id) {
            supabase.from('profiles').upsert({ id: user.id, preferred_language: lng }).then();
          }
        }}
        aria-label={t('chatbot.selectLanguage')}
        className="language-select"
      >
        {languages.map((lang) => (
          <option key={lang} value={lang}>
            {t(`chatbot.languages.${lang}`)}
          </option>
        ))}
      </select>
    </div>
  );
};

const ChatInterface = ({ messages, input, setInput, handleSend, handleKeyPress, showLoginForm, setShowLoginForm }) => {
  const { t } = useTranslation();
  const messagesEndRef = useRef(null);
  const { isAuthenticated, user, logout } = useAuth();
  
  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>{t('chatbot.title')}</h2>
        <div className="chat-controls">
          <LanguageSwitcher />
          {isAuthenticated ? (
            <button className="auth-button" onClick={logout}>
              {t('chatbot.logout')} ({user?.name})
            </button>
          ) : (
            <button className="auth-button" onClick={() => setShowLoginForm(true)}>
              {t('chatbot.login')}
            </button>
          )}
        </div>
      </div>
      
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder={t('chatbot.placeholder')}
          className="chat-input"
        />
        <button onClick={handleSend} className="send-button">
          {t('chatbot.sendButton')}
        </button>
      </div>
    </div>
  );
};



const ChatbotContainer = () => {
  const { t, i18n } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [input, setInput] = useState('');
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const { isAuthenticated, role } = useAuth();

  // Initialize session ID for analytics tracking if not exists
  useEffect(() => {
    if (!localStorage.getItem('session_id')) {
      localStorage.setItem('session_id', `session_${Date.now()}`);
    }
  }, []);

  // Initialize with welcome message translated based on current language
  useEffect(() => {
    setMessages([{ sender: 'bot', text: t('chatbot.welcomeMessage') }]);
  }, [t]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    // Log user event to Supabase
    logEvent({
      session_id: localStorage.getItem('session_id') || 'anonymous',
      sender: 'user',
      message_text: input,
      intent: null,
      timestamp: new Date().toISOString(),
    });
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    
    // Store user message and timestamp for analytics
    const messageWithMetadata = { 
      ...userMessage, 
      timestamp: new Date().toISOString(),
      sessionId: localStorage.getItem('session_id') || 'anonymous'
    };

    try {
      // Send current language to Rasa for potential multilingual processing
      const res = await fetch(`${RASA_BASE_URL}/webhooks/rest/webhook`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept-Language': i18n.language,
          ...(localStorage.getItem('auth_token') && { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` })
        },
        body: JSON.stringify({ 
          sender: isAuthenticated ? localStorage.getItem('auth_token') : 'guest-user',
          message: currentInput
        }),
      });
      
      const data = await res.json();
      if (Array.isArray(data)) {
        const now = Date.now();
        data.forEach((msg) => {
          if (msg.text) {
            const botMsg = {
              sender: 'bot',
              text: msg.text,
              intent: msg.intent || 'unknown',
              confidence: msg.confidence || 0
            };
            setMessages((prev) => [...prev, botMsg]);

            // Log bot event
            logEvent({
              session_id: localStorage.getItem('session_id') || 'anonymous',
              sender: 'bot',
              message_text: botMsg.text,
              intent: botMsg.intent,
              timestamp: new Date().toISOString(),
            });

            // Show feedback prompt on goodbye or fallback intents
            if (['goodbye', 'nlu_fallback'].includes(botMsg.intent)) {
              setShowFeedback(true);
            }
          }
        });
      }
    } catch (err) {
      console.error('Error communicating with Rasa backend:', err);
      setMessages((prev) => [...prev, { sender: 'bot', text: t('chatbot.errorMessage') }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="chatbot-container">
      {showLoginForm ? (
        <LoginForm onSuccess={() => setShowLoginForm(false)} />
      ) : showAnalytics && isAuthenticated && role === 'admin' ? (
        <>
          <Analytics conversationHistory={messages} />
          <button 
            className="toggle-view-button"
            onClick={() => setShowAnalytics(false)}
          >
            {t('chatbot.backToChat')}
          </button>
        </>
      ) : (
        <>
          <ChatInterface 
            messages={messages}
            input={input}
            setInput={setInput}
            handleSend={handleSend}
            handleKeyPress={handleKeyPress}
            showLoginForm={showLoginForm}
            setShowLoginForm={setShowLoginForm}
          />
          {isAuthenticated && role === 'admin' && (
            <button 
              className="toggle-view-button"
              onClick={() => setShowAnalytics(true)}
              aria-label={t('chatbot.viewAnalytics')}
            >
              {t('chatbot.viewAnalytics')}
            </button>
          )}
        </>
      )}
        {showFeedback && (
          <Feedback
            sessionId={localStorage.getItem('session_id') || 'anonymous'}
            onClose={() => setShowFeedback(false)}
          />
        )}
    </div>
  );
};

const Chatbot = () => {
  return (
    <AuthProvider>
      <ChatbotContainer />
    </AuthProvider>
  );
};

export default Chatbot;
