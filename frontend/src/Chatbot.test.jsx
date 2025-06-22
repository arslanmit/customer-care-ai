import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chatbot from './Chatbot.jsx';

// No longer need to mock i18n/translations since we're English-only now

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

  // Language switching test removed since we're English-only now
});
