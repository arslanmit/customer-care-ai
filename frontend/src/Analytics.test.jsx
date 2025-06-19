import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import Analytics from './Analytics.jsx';

// Mock Chart.js 
vi.mock('react-chartjs-2', () => ({
  Bar: () => <div data-testid="bar-chart" />,
  Doughnut: () => <div data-testid="doughnut-chart" />,
}));

// Mock the i18n provider
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'analytics.title': 'Conversation Analytics',
        'analytics.messageStats': 'Message Statistics',
        'analytics.userMessages': 'User Messages',
        'analytics.botResponses': 'Bot Responses',
        'analytics.avgResponseTime': 'Average Response Time',
        'analytics.messageDistribution': 'Message Distribution',
        'analytics.intentDistribution': 'Intent Distribution',
        'analytics.intentTypes': 'Intent Types'
      };
      return translations[key] || key;
    }
  }),
}));

describe('Analytics Component', () => {
  const mockConversation = [
    { sender: 'user', text: 'Hello', timestamp: new Date().toISOString() },
    { 
      sender: 'bot', 
      text: 'Hi there!', 
      timestamp: new Date().toISOString(), 
      metadata: { intent: 'greet', confidence: 0.9 } 
    },
    { sender: 'user', text: 'What time is it?', timestamp: new Date().toISOString() },
    { 
      sender: 'bot', 
      text: 'It is 2:30 PM', 
      timestamp: new Date().toISOString(), 
      metadata: { intent: 'ask_time', confidence: 0.85 } 
    }
  ];

  beforeEach(() => {
    // Mock localStorage with conversation history
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(() => JSON.stringify(mockConversation)),
      },
      writable: true
    });
  });

  it('renders the analytics title', () => {
    render(<Analytics />);
    expect(screen.getByText('Conversation Analytics')).toBeInTheDocument();
  });

  it('displays message statistics section', () => {
    render(<Analytics />);
    expect(screen.getByText('Message Statistics')).toBeInTheDocument();
    expect(screen.getByText('User Messages')).toBeInTheDocument();
    expect(screen.getByText('Bot Responses')).toBeInTheDocument();
    expect(screen.getByText('Average Response Time')).toBeInTheDocument();
  });

  it('renders message distribution chart', () => {
    render(<Analytics />);
    expect(screen.getByText('Message Distribution')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('renders intent distribution chart', () => {
    render(<Analytics />);
    expect(screen.getByText('Intent Distribution')).toBeInTheDocument();
    expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument();
  });

  it('displays correct message counts from conversation history', () => {
    render(<Analytics />);
    
    // We have 2 user messages and 2 bot responses in our mock data
    const userMessageCount = screen.getAllByText(/2/)[0];
    expect(userMessageCount).toBeInTheDocument();
    
    const botResponseCount = screen.getAllByText(/2/)[1];
    expect(botResponseCount).toBeInTheDocument();
  });
  
  it('handles empty conversation history gracefully', () => {
    // Override the localStorage mock to return null
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(() => null),
      },
      writable: true
    });
    
    render(<Analytics />);
    
    // The component should still render without errors
    expect(screen.getByText('Conversation Analytics')).toBeInTheDocument();
    
    // Charts should still be rendered with default/empty data
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument();
  });
});
