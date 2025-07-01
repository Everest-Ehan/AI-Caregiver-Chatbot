import React, { useState, useRef } from 'react';

export default function MessageInput({ onSend, onFocus }) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  // Expose focus function to parent component
  React.useImperativeHandle(onFocus, () => ({
    focus: () => inputRef.current && inputRef.current.focus()
  }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const value = input.trim();
    if (value) {
      onSend(value);
      setInput('');
      inputRef.current && inputRef.current.focus();
    }
  };

  return (
    <form className="chatbot-input-form" autoComplete="off" onSubmit={handleSubmit}>
      <input
        type="text"
        className="chatbot-input"
        placeholder="Type your message..."
        aria-label="Type your message"
        required
        value={input}
        onChange={e => setInput(e.target.value)}
        ref={inputRef}
      />
      <button type="submit" className="chatbot-send-btn">Send</button>
    </form>
  );
} 