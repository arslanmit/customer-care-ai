import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Auth from './Auth.jsx';

// Mock the i18n provider
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'auth.login': 'Login',
        'auth.register': 'Create Account',
        'auth.email': 'Email',
        'auth.password': 'Password',
        'auth.name': 'Name',
        'auth.loginToggle': 'Already have an account? Login',
        'auth.registerToggle': 'Need an account? Register',
        'auth.demoCredentials': 'Demo credentials:',
        'auth.demoEmail': 'Email: user@example.com',
        'auth.demoPassword': 'Password: password',
        'auth.emailRequired': 'Email is required',
        'auth.passwordRequired': 'Password is required',
        'auth.nameRequired': 'Name is required'
      };
      return translations[key] || key;
    }
  }),
}));

// Create a mock for the user context provider
const mockSetUserData = vi.fn();
vi.mock('./AuthContext', () => ({
  useAuth: () => ({
    userData: null, 
    setUserData: mockSetUserData
  })
}));

describe('Auth Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      },
      writable: true
    });
  });

  it('renders login form by default', () => {
    render(<Auth />);
    
    // Login form elements should be visible
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
    
    // Register toggle should be visible
    expect(screen.getByText('Need an account? Register')).toBeInTheDocument();
    
    // Name field should not be visible in login mode
    expect(screen.queryByLabelText('Name')).not.toBeInTheDocument();
  });

  it('switches to register form when toggle is clicked', async () => {
    const user = userEvent.setup();
    render(<Auth />);
    
    // Click register toggle
    await user.click(screen.getByText('Need an account? Register'));
    
    // Register form elements should be visible
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
    
    // Login toggle should be visible
    expect(screen.getByText('Already have an account? Login')).toBeInTheDocument();
  });

  it('validates email and password on login submission', async () => {
    const user = userEvent.setup();
    render(<Auth />);
    
    // Submit form without filling fields
    await user.click(screen.getByRole('button', { name: 'Login' }));
    
    // Validation error messages should appear
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
  });

  it('validates all fields on register submission', async () => {
    const user = userEvent.setup();
    render(<Auth />);
    
    // Switch to register mode
    await user.click(screen.getByText('Need an account? Register'));
    
    // Submit form without filling fields
    await user.click(screen.getByRole('button', { name: 'Create Account' }));
    
    // Validation error messages should appear
    expect(screen.getByText('Name is required')).toBeInTheDocument();
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
  });

  it('successfully logs in with valid credentials', async () => {
    const user = userEvent.setup();
    render(<Auth />);
    
    // Fill in login form
    await user.type(screen.getByLabelText('Email'), 'user@example.com');
    await user.type(screen.getByLabelText('Password'), 'password');
    
    // Submit form
    await user.click(screen.getByRole('button', { name: 'Login' }));
    
    // Wait for authentication to complete
    await waitFor(() => {
      expect(mockSetUserData).toHaveBeenCalledWith(expect.objectContaining({
        name: expect.any(String),
        email: 'user@example.com',
        token: expect.any(String)
      }));
      
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        'authToken',
        expect.any(String)
      );
    });
  });
});
