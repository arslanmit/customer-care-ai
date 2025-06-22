import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, renderHook } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './Auth.jsx';

// Test component that uses the auth context
const TestComponent = () => {
  const { isAuthenticated, user, login, logout, register } = useAuth();
  return (
    <div>
      <div data-testid="isAuthenticated">{isAuthenticated ? 'true' : 'false'}</div>
      <div data-testid="user">{JSON.stringify(user)}</div>
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={() => register('Test User', 'test@example.com', 'password')}>Register</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

// Helper component to render the auth provider with test component
const renderAuthProvider = () => {
  return render(
    <AuthProvider>
      <TestComponent />
    </AuthProvider>
  );
};

describe('Auth Context', () => {
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };

  beforeEach(() => {
    // Mock fetch for API calls
    global.fetch = vi.fn((url, opts) => {
      if (url.endsWith('/login') || url.endsWith('/register')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ access_token: 'mock-token' }) });
      }
      if (url.endsWith('/me')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'user@example.com', role: 'user' }) });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({ detail: 'not found' }) });
    });
    // Clear all mocks and localStorage before each test
    vi.clearAllMocks();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true
    });
  });

  afterEach(() => {
    // Cleanup
    vi.restoreAllMocks();
    global.fetch.mockRestore && global.fetch.mockRestore();
  });

  it('provides initial auth state', () => {
    renderAuthProvider();

    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('user')).toHaveTextContent('null');
  });

  it('handles login successfully', async () => {
    const user = userEvent.setup();
    renderAuthProvider();

    // Mock successful login
    localStorageMock.getItem.mockReturnValueOnce('mock-token');
    
    // Click login button with valid credentials
    await user.click(screen.getByText('Login'));
    
    // Wait for the login to complete
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });
    
    // Check that user data is set
    const userData = JSON.parse(screen.getByTestId('user').textContent);
    expect(userData).toMatchObject({
      id: '1',
      name: 'Demo User',
      email: 'test@example.com'
    });
    
    // Check that auth token was stored in localStorage
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', expect.any(String));
  });

  it('handles login failure', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    renderAuthProvider();

    // Mock a failed login
    localStorageMock.getItem.mockReturnValueOnce(null);
    
    // Click login button with invalid credentials
    await user.click(screen.getByText('Login'));
    
    // Should still be logged out
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
    
    // Error should be logged
    expect(consoleSpy).toHaveBeenCalledWith('Login error:', expect.any(Error));
    consoleSpy.mockRestore();
  });

  it('handles registration successfully', async () => {
    const user = userEvent.setup();
    renderAuthProvider();

    // Click register button with valid data
    await user.click(screen.getByText('Register'));
    
    // Wait for the registration to complete
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });
    
    // Check that user data is set
    const userData = JSON.parse(screen.getByTestId('user').textContent);
    expect(userData).toMatchObject({
      id: expect.any(String),
      name: 'Test User',
      email: 'test@example.com'
    });
    
    // Check that auth token was stored in localStorage
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', expect.any(String));
  });

  it('validates registration data', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    renderAuthProvider();

    // Mock a failed registration with invalid data
    localStorageMock.setItem.mockImplementationOnce(() => {
      throw new Error('Invalid email or password (min 6 characters)');
    });
    
    // Click register button
    await user.click(screen.getByText('Register'));
    
    // Should still be logged out
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
    
    // Error should be logged
    expect(consoleSpy).toHaveBeenCalledWith(
      'Registration error:', 
      expect.any(Error)
    );
    consoleSpy.mockRestore();
  });

  it('handles logout', async () => {
    const user = userEvent.setup();
    renderAuthProvider();

    // Login first
    await user.click(screen.getByText('Login'));
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });
    
    // Now logout
    await user.click(screen.getByText('Logout'));
    
    // Should be logged out
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('null');
    });
    
    // Check that auth token was removed from localStorage
    expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
  });

  it('restores session from localStorage on mount', async () => {
    // Mock existing token in localStorage
    const mockToken = 'existing-token';
    localStorageMock.getItem.mockImplementation((key) => {
      return key === 'auth_token' ? mockToken : null;
    });
    
    renderAuthProvider();
    
    // Should be authenticated with the existing token
    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });
    
    // Should have user data
    const userData = JSON.parse(screen.getByTestId('user').textContent);
    expect(userData).toMatchObject({
      id: '1',
      name: 'Demo User',
      email: 'user@example.com'
    });
  });
});
