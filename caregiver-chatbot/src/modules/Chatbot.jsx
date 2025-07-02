import React, { useState, useEffect, useRef } from 'react';
import ChatbotEngine from './ChatbotEngine.jsx';
import ScenarioSelector from './ScenarioSelector.jsx';
import MessageList from './MessageList.jsx';
import MessageInput from './MessageInput.jsx';
import QuickResponses from './QuickResponses.jsx';

export default function Chatbot() {
  const [engine] = useState(() => new ChatbotEngine());
  const [allScenarios, setAllScenarios] = useState([]);
  const [currentScenario, setCurrentScenario] = useState(null);
  const [messages, setMessages] = useState([]);
  const [context, setContext] = useState({});
  const [showQuickResponses, setShowQuickResponses] = useState(false);
  const [contextFields, setContextFields] = useState([]);
  const [isScenarioSelectorExpanded, setIsScenarioSelectorExpanded] = useState(true);
  const [messageInputValue, setMessageInputValue] = useState("");
  const messageInputRef = useRef(null);

  // Load scenarios on mount
  useEffect(() => {
    async function loadScenarios() {
      const scenarios = await engine.getAvailableScenarios();
      setAllScenarios(scenarios);
    }
    loadScenarios();
  }, [engine]);

  // Update context when engine context changes
  useEffect(() => {
    engine.onContextUpdate = () => {
      setContext({ ...engine.context });
    };
  }, [engine]);

  // Handle scenario selection
  const handleScenarioSelect = async (scenarioId) => {
    setShowQuickResponses(false);
    setMessages([]);
    setCurrentScenario(scenarioId);
    setIsScenarioSelectorExpanded(false); // Collapse the scenario selector
    
    // Clear context when scenario is selected
    setContext({});
    
    const response = await engine.startScenario(scenarioId);
    setMessages([{ sender: 'agent', text: response.message, timestamp: new Date().toISOString() }]);
    setShowQuickResponses(true);
    
    // Focus the message input after scenario starts
    setTimeout(() => {
      messageInputRef.current?.focus();
    }, 100);
  };

  // Handle sending a message
  const handleSend = async (msg) => {
    setMessages(prev => [...prev, { sender: 'user', text: msg, timestamp: new Date().toISOString() }]);
    setMessageInputValue(""); // Clear input after sending
    const response = await engine.processUserInput(msg);
    setMessages(prev => [...prev, { sender: 'agent', text: response.message, timestamp: new Date().toISOString() }]);
  };

  // Handle quick response selection
  const handleQuickResponse = (response) => {
    setMessageInputValue(prev => {
      const sep = prev && !prev.endsWith(' ') ? ' ' : '';
      return prev + sep + response;
    });
    if (messageInputRef.current && typeof messageInputRef.current.focus === 'function') {
      messageInputRef.current.focus();
    }
  };

  // Build a master list of all possible context fields from all scenarios
  useEffect(() => {
    if (currentScenario && typeof currentScenario === 'object') {
      // If currentScenario is an object from backend, use its context_fields
      const fields = currentScenario.context_fields || [];
      let allFields = {};
      fields.forEach(field => {
        allFields[field] = {
          label: field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          placeholder: `Enter ${field.replace(/_/g, ' ').toLowerCase()}`,
          required: false
        };
      });
      setContextFields(allFields);
    } else if (typeof currentScenario === 'string') {
      // If currentScenario is just an id, find the scenario object
      const scenarioObj = allScenarios.find(s => s.id === currentScenario);
      if (scenarioObj && scenarioObj.context_fields) {
        let allFields = {};
        scenarioObj.context_fields.forEach(field => {
          allFields[field] = {
            label: field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            placeholder: `Enter ${field.replace(/_/g, ' ').toLowerCase()}`,
            required: false
          };
        });
        setContextFields(allFields);
      } else {
        setContextFields({});
      }
    } else {
      setContextFields({});
    }
  }, [currentScenario, allScenarios]);

  // Handle context field change
  const handleContextChange = (key, value) => {
    engine.updateContext({ [key]: value });
    setContext(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-main-layout">
        {/* Left Panel */}
        <div className="chatbot-left-panel">
          <ScenarioSelector 
            scenarios={allScenarios} 
            onScenarioSelect={handleScenarioSelect}
            isExpanded={isScenarioSelectorExpanded}
            onToggleExpanded={() => setIsScenarioSelectorExpanded(!isScenarioSelectorExpanded)}
          />
          {showQuickResponses && <QuickResponses onResponseSelect={handleQuickResponse} />}
        </div>
        {/* Center Panel */}
        <div className="chatbot-center-panel">
          <div className="chatbot-header">
            <div className="chatbot-title">Caregiver Support Chat</div>
            <div className="chatbot-subtitle">Professional Assistance</div>
          </div>
          <MessageList messages={messages} />
          <MessageInput 
            onSend={handleSend} 
            onFocus={messageInputRef} 
            value={messageInputValue}
            onChange={e => setMessageInputValue(e.target.value)}
          />
        </div>
        {/* Right Panel - Context */}
        <div className="chatbot-right-panel">
          <div className="context-section">
            <div className="panel-header">
              <h3>Context Settings</h3>
              <p>Configure conversation details</p>
            </div>
            <div className="context-inputs">
              {Object.entries(contextFields).map(([key, config]) => (
                <div className="input-group" key={key}>
                  <label>{config.label || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                  <input
                    type="text"
                    id={key}
                    value={context[key] || ''}
                    placeholder={config.placeholder || `Enter ${key}`}
                    onChange={e => handleContextChange(key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}