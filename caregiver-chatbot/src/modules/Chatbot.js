import ChatbotEngine from './ChatbotEngine.js';
import ScenarioSelector from './ScenarioSelector.js';
import MessageList from './MessageList.js';
import MessageInput from './MessageInput.js';
import QuickResponses from './QuickResponses.js';

export default function Chatbot() {
  const container = document.createElement('div');
  container.className = 'chatbot-container';

  const engine = new ChatbotEngine();
  let currentScenario = null;

  // Main Layout
  const mainLayout = document.createElement('div');
  mainLayout.className = 'chatbot-main-layout';

  // Left Panel - Scenario Selector & Quick Responses
  const leftPanel = document.createElement('div');
  leftPanel.className = 'chatbot-left-panel';
  
  // Scenario Selector (Card UI, initially expanded)
  const scenarioSelectorContainer = document.createElement('div');
  scenarioSelectorContainer.className = 'scenario-selector-container expanded';

  const scenarioSelectorHeader = document.createElement('div');
  scenarioSelectorHeader.className = 'scenario-selector-header';
  scenarioSelectorHeader.innerHTML = `
    <h3 class="scenario-selector-title">Select Scenario</h3>
    <button class="scenario-selector-toggle">Change Scenario</button>
  `;

  const scenarioSelectorContent = document.createElement('div');
  scenarioSelectorContent.className = 'scenario-selector-content';

  // Add a prominent message when no scenario is selected
  const noScenarioMessage = document.createElement('div');
  noScenarioMessage.style.cssText = `
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 16px;
    margin-bottom: 20px;
    border: 2px solid rgba(14, 165, 233, 0.2);
  `;
  noScenarioMessage.innerHTML = `
    <h4 style="color: #0ea5e9; margin: 0 0 8px 0; font-size: 1.1rem;">Choose Your Scenario</h4>
    <p style="color: #64748b; margin: 0; font-size: 0.95rem;">Select one of the scenarios below to begin your conversation</p>
  `;

  // Card UI for scenarios
  async function renderScenarioCards(scenarios) {
    scenarioSelectorContent.innerHTML = '';
    scenarioSelectorContent.appendChild(noScenarioMessage);
    scenarios.forEach(scenario => {
      const card = document.createElement('div');
      card.className = 'scenario-card';
      card.innerHTML = `
        <div class="scenario-card-content">
          <h4>${scenario.name}</h4>
          <p>${scenario.description}</p>
        </div>
      `;
      card.addEventListener('click', async () => {
        scenarioSelectorContent.querySelectorAll('.scenario-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        
        // Show loading state
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'loading-message';
        loadingMessage.innerHTML = `
          <div class="loading-spinner"></div>
          <p>Starting conversation...</p>
        `;
        messageList.addMessage({
          sender: 'system',
          text: 'Loading...',
          timestamp: new Date().toISOString()
        });
        
        try {
          // On select - use async engine
          const response = await engine.startScenario(scenario.id);
          currentScenario = scenario.id;
          messageList.clear();
          messageList.addMessage({
            sender: 'agent',
            text: response.message,
            timestamp: new Date().toISOString()
          });
          
          // Wait a bit for the scenario to be set, then update context fields
          setTimeout(() => {
            updateContextFields(scenario.id);
          }, 100);
          
          const scenarioObj = await engine.getCurrentScenario();
          if (scenarioObj) {
            scenarioSelectorHeader.querySelector('.scenario-selector-title').textContent = scenarioObj.name;
          }
          // Collapse scenario selector after selection
          scenarioSelectorContainer.classList.remove('expanded');
          // Show quick responses after scenario selection
          quickResponses.element.style.display = 'block';
          enableChatInput();
          showChatInterface();
          messageInput.focus();
        } catch (error) {
          console.error('Error starting scenario:', error);
          messageList.clear();
          messageList.addMessage({
            sender: 'system',
            text: 'Sorry, there was an error starting the conversation. Please try again.',
            timestamp: new Date().toISOString()
          });
        }
      });
      scenarioSelectorContent.appendChild(card);
    });
  }

  // Get scenarios from engine and render
  async function loadScenarios() {
    try {
      const availableScenarios = await engine.getAvailableScenarios();
      renderScenarioCards(availableScenarios);
    } catch (error) {
      console.error('Error loading scenarios:', error);
      // Fallback to empty scenarios
      renderScenarioCards([]);
    }
  }
  
  // Load scenarios on initialization
  loadScenarios();

  scenarioSelectorContainer.appendChild(scenarioSelectorHeader);
  scenarioSelectorContainer.appendChild(scenarioSelectorContent);

  // Toggle scenario selector - header click
  scenarioSelectorHeader.addEventListener('click', (e) => {
    // Don't toggle if clicking on the toggle button (it has its own handler)
    if (e.target.classList.contains('scenario-selector-toggle')) {
      return;
    }
    // Toggle the expanded state
    scenarioSelectorContainer.classList.toggle('expanded');
    updateToggleButtonText();
  });

  // Toggle scenario selector - button click
  const toggleButton = scenarioSelectorHeader.querySelector('.scenario-selector-toggle');
  toggleButton.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent header click event
    scenarioSelectorContainer.classList.toggle('expanded');
    updateToggleButtonText();
  });

  // Function to update toggle button text
  function updateToggleButtonText() {
    const isExpanded = scenarioSelectorContainer.classList.contains('expanded');
    toggleButton.textContent = isExpanded ? 'Collapse' : 'Expand';
  }

  // Initialize button text
  updateToggleButtonText();

  // Quick Responses (Initially Hidden)
  const quickResponses = QuickResponses((response) => {
    messageInput.setValue(response);
  });
  quickResponses.element.style.display = 'none'; // Initially hidden

  // Add scenario selector and quick responses to left panel
  leftPanel.appendChild(scenarioSelectorContainer);
  leftPanel.appendChild(quickResponses.element);

  // Center Panel - Chat
  const centerPanel = document.createElement('div');
  centerPanel.className = 'chatbot-center-panel';
  
  const chatHeader = document.createElement('div');
  chatHeader.className = 'chatbot-header';
  chatHeader.innerHTML = `
    <div class="chatbot-title">Caregiver Support Chat</div>
    <div class="chatbot-subtitle">Professional Assistance</div>
  `;

  const messageList = MessageList();
  const messageInput = MessageInput((msg) => {
    if (!currentScenario) {
      messageInput.element.querySelector('input').disabled = true;
      messageInput.element.querySelector('button').disabled = true;
      messageList.addMessage({
        sender: 'agent',
        text: 'Please select a scenario to begin.',
        timestamp: new Date().toISOString()
      });
      return;
    }

    // Add user message
    messageList.addMessage({
      sender: 'user',
      text: msg,
      timestamp: new Date().toISOString()
    });

    // Process with engine
    const response = engine.processUserInput(msg);
    
    // Add agent response
    messageList.addMessage({
      sender: 'agent',
      text: response.message,
      timestamp: new Date().toISOString()
    });

    if (response.isComplete) {
      currentScenario = null;
      // Show scenario selector again after a delay
      setTimeout(() => {
        showScenarioSelector();
      }, 2000);
    }
  });

  // Disable chat input until scenario is selected
  messageInput.element.querySelector('input').disabled = true;
  messageInput.element.querySelector('button').disabled = true;

  // When scenario is selected, enable chat input
  function enableChatInput() {
    messageInput.element.querySelector('input').disabled = false;
    messageInput.element.querySelector('button').disabled = false;
  }

  centerPanel.appendChild(chatHeader);
  centerPanel.appendChild(messageList.element);
  centerPanel.appendChild(messageInput.element);

  // Right Panel - Context
  const rightPanel = document.createElement('div');
  rightPanel.className = 'chatbot-right-panel';

  // Context Settings
  const contextSection = document.createElement('div');
  contextSection.className = 'context-section';
  contextSection.innerHTML = `
    <div class="panel-header">
      <h3>Context Settings</h3>
      <p>Configure conversation details</p>
    </div>
    <div class="context-inputs" id="contextInputs">
      <!-- Dynamic context fields will be inserted here -->
    </div>
  `;

  rightPanel.appendChild(contextSection);

  // Assemble Layout
  mainLayout.appendChild(leftPanel);
  mainLayout.appendChild(centerPanel);
  mainLayout.appendChild(rightPanel);
  container.appendChild(mainLayout);

  // Initialize
  // scenarioSelector.updateScenarios(engine.getAvailableScenarios());

  function updateContextFields(scenarioId) {
    const contextInputsContainer = contextSection.querySelector('#contextInputs');
    
    console.log('updateContextFields called with scenarioId:', scenarioId);
    console.log('Current scenario:', engine.getCurrentScenario());
    
    // Get context fields from the engine
    const contextFields = engine.getCurrentScenarioContextFields();
    console.log('Context fields:', contextFields);
    
    if (!contextFields || Object.keys(contextFields).length === 0) {
      console.log('No context fields found, showing default message');
      contextInputsContainer.innerHTML = `
        <div class="input-group">
          <label>Select a scenario to see relevant context fields</label>
          <input type="text" disabled placeholder="No scenario selected">
        </div>
      `;
      return;
    }

    // Clear existing inputs
    contextInputsContainer.innerHTML = '';

    // Create inputs for each context field
    Object.entries(contextFields).forEach(([fieldKey, fieldConfig]) => {
      const inputGroup = document.createElement('div');
      inputGroup.className = 'input-group';
      
      const label = document.createElement('label');
      label.textContent = fieldConfig.label;
      if (fieldConfig.required) {
        label.innerHTML += ' <span style="color: #ef4444;">*</span>';
      }
      
      const input = document.createElement('input');
      input.type = 'text';
      input.id = fieldKey;
      input.placeholder = fieldConfig.placeholder || `Enter ${fieldConfig.label.toLowerCase()}`;
      input.required = fieldConfig.required;
      
      // Set default value if available in engine context
      // Try both the original field key and converted context key
      const contextKey = fieldKey.replace(/([A-Z])/g, '_$1').toLowerCase();
      if (engine.context[fieldKey]) {
        input.value = engine.context[fieldKey];
      } else if (engine.context[contextKey]) {
        input.value = engine.context[contextKey];
      }
      
      // Add change event listener
      input.addEventListener('change', () => {
        updateEngineContext();
      });
      
      inputGroup.appendChild(label);
      inputGroup.appendChild(input);
      contextInputsContainer.appendChild(inputGroup);
    });
  }

  function updateEngineContext() {
    const contextInputsContainer = contextSection.querySelector('#contextInputs');
    const inputs = contextInputsContainer.querySelectorAll('input');
    const newContext = {};
    
    inputs.forEach(input => {
      if (input.value.trim()) {
        // Store both the original field key and converted context key
        newContext[input.id] = input.value.trim();
        const contextKey = input.id.replace(/([A-Z])/g, '_$1').toLowerCase();
        newContext[contextKey] = input.value.trim();
      }
    });
    
    engine.updateContext(newContext);
  }

  function showScenarioSelector() {
    // Reset to initial state
    currentScenario = null;
    messageList.clear();
    updateContextFields(null);
    
    // Reset scenario selector header
    scenarioSelectorHeader.querySelector('.scenario-selector-title').textContent = 'Select Scenario';
    
    // Hide quick responses
    quickResponses.element.style.display = 'none';
    
    // Re-render scenario cards
    loadScenarios();
    
    // Expand scenario selector
    scenarioSelectorContainer.classList.add('expanded');
  }

  function showChatInterface() {
    // Chat interface is always visible in center panel
  }

  // Handle message input
  const inputElement = messageInput.element.querySelector('input');
  const formElement = messageInput.element;
  
  inputElement.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const message = inputElement.value.trim();
      if (!message) return;

      // Disable input while processing
      inputElement.disabled = true;
      inputElement.value = '';

      // Add user message
      messageList.addMessage({
        sender: 'user',
        text: message,
        timestamp: new Date().toISOString()
      });

      // Show typing indicator
      const typingIndicator = messageList.addTypingIndicator();

      try {
        // Process with engine (now async)
        const response = await engine.processUserInput(message);
        
        // Remove typing indicator
        messageList.removeTypingIndicator(typingIndicator);

        // Add agent response
        messageList.addMessage({
          sender: 'agent',
          text: response.message,
          timestamp: new Date().toISOString()
        });

        // Check if conversation is complete
        if (response.isComplete) {
          disableChatInput();
          // Show completion message or extracted data
          if (response.extractedData) {
            console.log('Extracted data:', response.extractedData);
            // You could display this data in a summary panel
          }
        }
      } catch (error) {
        console.error('Error processing message:', error);
        messageList.removeTypingIndicator(typingIndicator);
        messageList.addMessage({
          sender: 'system',
          text: 'Sorry, there was an error processing your message. Please try again.',
          timestamp: new Date().toISOString()
        });
      } finally {
        // Re-enable input
        inputElement.disabled = false;
        inputElement.focus();
      }
    }
  });

  return container;
}