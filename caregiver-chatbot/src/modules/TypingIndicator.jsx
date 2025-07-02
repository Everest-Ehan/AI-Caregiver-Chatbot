import React from 'react';
import '../styles/TypingIndicator.css';

const TypingIndicator = () => (
  <div className="chatbot-message chatbot-message--agent chatbot-message--typing">
    <div className="chatbot-message-meta">
      <span className="chatbot-message-sender">Support</span>
    </div>
    <div className="chatbot-message-text">
      <div className="typing-indicator">
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
      </div>
    </div>
  </div>
);

export default TypingIndicator; 