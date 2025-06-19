import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Chatbot from './Chatbot.jsx';

// Mock the global fetch function before each test
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve([{ text: 'Hi there!' }]),
    })
  );
});

afterEach(() => {
  jest.resetAllMocks();
});

test('user message appears and bot response is added', async () => {
  render(<Chatbot />);

  const input = screen.getByPlaceholderText(/Type your message/i);
  const sendButton = screen.getByText(/Send/i);

  // Type a message
  fireEvent.change(input, { target: { value: 'hello' } });
  // Click send
  fireEvent.click(sendButton);

  // User message should immediately appear
  expect(screen.getByText('hello')).toBeInTheDocument();

  // Wait for mocked bot response to appear
  await waitFor(() => expect(screen.getByText('Hi there!')).toBeInTheDocument());
});
