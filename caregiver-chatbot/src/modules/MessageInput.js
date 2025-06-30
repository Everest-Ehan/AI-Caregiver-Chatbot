export default function MessageInput(onSend) {
  const element = document.createElement('form');
  element.className = 'chatbot-input-form';
  element.autocomplete = 'off';

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'chatbot-input';
  input.placeholder = 'Type your message...';
  input.setAttribute('aria-label', 'Type your message');
  input.required = true;

  const button = document.createElement('button');
  button.type = 'submit';
  button.className = 'chatbot-send-btn';
  button.textContent = 'Send';

  element.appendChild(input);
  element.appendChild(button);

  element.addEventListener('submit', (e) => {
    e.preventDefault();
    const value = input.value.trim();
    if (value) {
      onSend(value);
      input.value = '';
      input.focus();
    }
  });

  function setValue(value) {
    input.value = value;
    input.focus();
  }

  function focus() {
    input.focus();
  }

  return {
    element,
    setValue,
    focus
  };
} 