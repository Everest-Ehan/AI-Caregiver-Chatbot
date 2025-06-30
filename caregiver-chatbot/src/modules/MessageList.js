export default function MessageList(initialMessages = []) {
  const element = document.createElement('div');
  element.className = 'chatbot-messages';

  let messages = [...initialMessages];

  function render() {
    element.innerHTML = '';
    messages.forEach(msg => {
      const msgDiv = document.createElement('div');
      msgDiv.className = `chatbot-message chatbot-message--${msg.sender}`;
      msgDiv.innerHTML = `
        <div class="chatbot-message-meta">
          <span class="chatbot-message-sender">${msg.sender === 'agent' ? 'Support' : 'You'}</span>
          <span class="chatbot-message-time">${formatTime(msg.timestamp)}</span>
        </div>
        <div class="chatbot-message-text">${escapeHTML(msg.text)}</div>
      `;
      element.appendChild(msgDiv);
    });
    element.scrollTop = element.scrollHeight;
  }

  function addMessage(msg) {
    messages.push(msg);
    render();
  }

  function clear() {
    messages = [];
    render();
  }

  function getMessages() {
    return [...messages];
  }

  render();

  return {
    element,
    addMessage,
    clear,
    getMessages
  };
}

function formatTime(iso) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, tag => ({'&':'&amp;','<':'&lt;','>':'&gt;','\'':'&#39;','"':'&quot;'}[tag]));
} 