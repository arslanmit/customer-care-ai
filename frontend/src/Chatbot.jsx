import React, { useState } from 'react';
import './chatbot.css';

const RASA_BASE_URL = import.meta.env.VITE_RASA_URL || "http://localhost:5005";

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! How can I assist you today?' },
  ]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');

    try {
      const res = await fetch(`${RASA_BASE_URL}/webhooks/rest/webhook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender: 'browser-user', message: currentInput }),
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        data.forEach((msg) => {
          if (msg.text) {
            setMessages((prev) => [...prev, { sender: 'bot', text: msg.text }]);
          }
        });
      }
    } catch (err) {
      console.error('Error communicating with Rasa backend:', err);
      setMessages((prev) => [...prev, { sender: 'bot', text: 'Sorry, something went wrong.' }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handlePaste = (e) => {
    const pasteData = e.clipboardData.getData('text');
    setInput(pasteData);
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;
