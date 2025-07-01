import React, { useEffect, useRef } from 'react';

function formatTime(iso) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, tag => ({'&':'&amp;','<':'&lt;','>':'&gt;','\'':'&#39;','"':'&quot;'}[tag]));
}

export default function MessageList({ messages }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chatbot-messages" ref={messagesEndRef}>
      {messages.map((msg, idx) => (
        <div key={idx} className={`chatbot-message chatbot-message--${msg.sender}`}>
          <div className="chatbot-message-meta">
            <span className="chatbot-message-sender">{msg.sender === 'agent' ? 'Support' : 'You'}</span>
            <span className="chatbot-message-time">{formatTime(msg.timestamp)}</span>
          </div>
          <div className="chatbot-message-text" dangerouslySetInnerHTML={{ __html: escapeHTML(msg.text) }} />
        </div>
      ))}
    </div>
  );
} 