import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chatbot from './Chatbot.jsx';

// Mock the useTranslation hook with specific translations for Chatbot
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'chatbot.placeholder': 'Type your message...',
        'chatbot.sendButton': 'Send',
        'chatbot.viewAnalytics': 'View Analytics',
        'chatbot.backToChat': 'Back to Chat',
        'chatbot.login': 'Login',
        'chatbot.logout': 'Logout',
        'chatbot.selectLanguage': 'Select language',
        'chatbot.welcome': 'Welcome to the Chatbot',
        'chatbot.errorSending': 'Error sending message',
        'chatbot.typing': 'typing...'
      };
      return translations[key] || key;
    },
    i18n: {
      changeLanguage: vi.fn(),
      language: 'en',
    },
  }),
}));

// Mock the AuthContext
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '123', name: 'Test User' },
    login: vi.fn(),
    logout: vi.fn(),
    isAuthenticated: true
  })
}));

// Mock localStorage
beforeEach(() => {
  // Setup localStorage mock
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    },
    writable: true,
  });
  
  // Mock fetch API
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve([{ text: 'Hi there!' }]),
    })
  );
});

afterEach(() => {
  vi.resetAllMocks();
});

describe('Chatbot Component', () => {
  it('renders the chatbot interface correctly', () => {
    render(<Chatbot />);
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  it('sends user message and receives bot response', async () => {
    const user = userEvent.setup();
    render(<Chatbot />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    // Type a message using userEvent for more realistic interaction
    await user.type(input, 'hello');
    await user.click(sendButton);

    // User message should immediately appear
    expect(screen.getByText('hello')).toBeInTheDocument();

    // Wait for mocked bot response to appear
    await waitFor(() => expect(screen.getByText('Hi there!')).toBeInTheDocument());
    
    // Verify fetch was called with the right parameters
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it('switches between chat and analytics views', async () => {
    const user = userEvent.setup();
    render(<Chatbot />);

    // Initially in chat view
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    
    // Click to view analytics
    const viewAnalyticsButton = screen.getByText('View Analytics');
    await user.click(viewAnalyticsButton);
    
    // Expect back to chat button to be present in analytics view
    expect(screen.getByText('Back to Chat')).toBeInTheDocument();
  });

  it('handles language switching', async () => {
    const user = userEvent.setup();
    render(<Chatbot />);

    // Find the language selector
    const languageSelect = screen.getByLabelText('Select language');
    expect(languageSelect).toBeInTheDocument();
    
    // Change language
    await user.selectOptions(languageSelect, 'es');
    
    // i18n change language should have been called
    const { i18n } = vi.mocked(useTranslation(), true)();
    expect(i18n.changeLanguage).toHaveBeenCalledWith('es');
  });
});
