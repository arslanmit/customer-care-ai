import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import Analytics from './Analytics.jsx';

// Mock react-chartjs-2
vi.mock('react-chartjs-2', () => ({
  Bar: () => <div data-testid="bar-chart">Bar Chart</div>,
  Pie: () => <div data-testid="pie-chart">Pie Chart</div>,
}));

// Mock the useTranslation hook with specific translations for Analytics
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key, // Return the key as the translation
    i18n: {
      language: 'en',
      changeLanguage: () => Promise.resolve(),
    },
  }),
}));

describe('Analytics Component', () => {
  const mockConversation = [
    { 
      sender: 'user', 
      text: 'Hello', 
      timestamp: new Date().toISOString(),
      intent: 'greet'
    },
    { 
      sender: 'bot', 
      text: 'Hi there!', 
      timestamp: new Date().toISOString(),
      intent: 'greet_response'
    },
    { 
      sender: 'user', 
      text: 'What time is it?', 
      timestamp: new Date().toISOString(),
      intent: 'ask_time'
    },
    { 
      sender: 'bot', 
      text: 'It is 2:30 PM', 
      timestamp: new Date().toISOString(),
      intent: 'time_response'
    }
  ];

  it('renders the analytics title', () => {
    render(<Analytics conversationHistory={mockConversation} />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('analytics.title');
  });

  it('displays message statistics section', () => {
    render(<Analytics conversationHistory={mockConversation} />);
    
    // Check for section headers
    expect(screen.getByText('analytics.messageStats')).toBeInTheDocument();
    
    // Check for message counts
    const userMessagesText = screen.getByText('analytics.userMessages').parentElement.textContent;
    const botResponsesText = screen.getByText('analytics.botResponses').parentElement.textContent;
    
    expect(parseInt(userMessagesText.match(/\d+/)[0])).toBeGreaterThan(0);
    expect(parseInt(botResponsesText.match(/\d+/)[0])).toBeGreaterThan(0);
  });

  it('renders message distribution chart', () => {
    render(<Analytics conversationHistory={mockConversation} />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('renders intent distribution chart', () => {
    render(<Analytics conversationHistory={mockConversation} />);
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });

  it('displays correct message counts from conversation history', () => {
    render(<Analytics conversationHistory={mockConversation} />);
    
    // Check for user messages and bot responses
    const userMessagesText = screen.getByText('analytics.userMessages').parentElement.textContent;
    const botResponsesText = screen.getByText('analytics.botResponses').parentElement.textContent;
    
    expect(parseInt(userMessagesText.match(/\d+/)[0])).toBe(2);
    expect(parseInt(botResponsesText.match(/\d+/)[0])).toBe(2);
  });
  
  it('handles empty conversation history gracefully', () => {
    render(<Analytics conversationHistory={[]} />);
    
    // Should still render the component without errors
    expect(screen.getByText('analytics.title')).toBeInTheDocument();
    
    // Should show no messages
    const userMessagesText = screen.getByText('analytics.userMessages').parentElement.textContent;
    const botResponsesText = screen.getByText('analytics.botResponses').parentElement.textContent;
    
    expect(parseInt(userMessagesText.match(/\d+/)[0])).toBe(0);
    expect(parseInt(botResponsesText.match(/\d+/)[0])).toBe(0);
    
    // Charts should still be rendered with default/empty data
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });
});
