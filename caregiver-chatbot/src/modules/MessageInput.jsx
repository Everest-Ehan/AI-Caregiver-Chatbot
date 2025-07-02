import React, { useRef } from 'react';

export default function MessageInput({ onSend, onFocus, value, onChange }) {
  const inputRef = useRef(null);

  // Expose focus function to parent component
  React.useImperativeHandle(onFocus, () => ({
    focus: () => inputRef.current && inputRef.current.focus()
  }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const val = (value !== undefined ? value : inputRef.current.value).trim();
    if (val) {
      onSend(val);
      if (onChange) onChange({ target: { value: '' } }); // Clear controlled input
      if (inputRef.current) inputRef.current.focus();
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
        value={value !== undefined ? value : undefined}
        onChange={onChange ? onChange : e => {}}
        ref={inputRef}
      />
      <button type="submit" className="chatbot-send-btn">Send</button>
    </form>
  );
}