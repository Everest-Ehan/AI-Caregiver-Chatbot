import { scenarios, responseMappings } from '../data/scenarios.js';
import apiService from '../services/api.jsx';
import LoadingScreen from './LoadingScreen';

export default class ChatbotEngine {
  constructor() {
    this.currentScenario = null;
    this.currentStep = 0;
    this.conversationHistory = [];
    this.context = {};
    this.useBackend = true; // Flag to control backend vs frontend processing
    this.sessionId = null;
    this.onContextUpdate = null; // Callback for UI updates
    this.checkBackendHealth();
    this.loading = false;
    this.onLoadingChange = null; // Callback for UI loading state
  }

  setLoading(val) {
    this.loading = val;
    if (this.onLoadingChange) this.onLoadingChange(val);
  }

  async startScenario(scenarioId) {
    this.setLoading(true);
    try {
      if (this.useBackend) {
        const sessionResponse = await apiService.startSession(scenarioId);
        this.sessionId = sessionResponse.session_id;
        const scenarios = await apiService.getScenarios();
        const scenario = scenarios.find(s => s.id === scenarioId);
        if (scenario) {
          this.currentScenario = scenario;
        }
        // Reset context for new scenario - start with empty context
        this.context = {};
        
        // Explicitly reset the backend context to ensure it's completely cleared
        await apiService.resetSessionContext(this.sessionId, {});
        
        const response = await apiService.sendMessage(
          "Hello, I need help with my issue",
          scenarioId,
          this.context
        );
        return {
          message: response.message,
          stepId: 'initial',
          isComplete: response.is_complete || false
        };
      } else {
        const scenario = scenarios[scenarioId];
        if (!scenario) {
          throw new Error(`Unknown scenario: ${scenarioId}`);
        }
        this.currentScenario = scenario;
        this.currentStep = 0;
        this.conversationHistory = [];
        const firstStep = scenario.steps[0];
        return {
          message: this.processMessage(firstStep.agent),
          stepId: firstStep.id,
          isComplete: false
        };
      }
    } catch (error) {
      console.error('Error starting scenario:', error);
      this.useBackend = false;
      return this.startScenario(scenarioId);
    } finally {
      this.setLoading(false);
    }
  }

  getCurrentScenarioContextFields() {
    if (!this.currentScenario) return {};
    if (this.useBackend && this.currentScenario.context_fields) {
      const contextFields = {};
      this.currentScenario.context_fields.forEach(field => {
        contextFields[field] = {
          label: field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          placeholder: `Enter ${field.replace(/_/g, ' ').toLowerCase()}`,
          type: 'text',
          required: false
        };
      });
      return contextFields;
    }
    return this.currentScenario.contextFields || {};
  }

  getCurrentScenario() {
    return this.currentScenario;
  }

  async processUserInput(userInput) {
    this.setLoading(true);
    try {
      if (this.useBackend) {
        const response = await apiService.sendMessage(
          userInput,
          this.currentScenario?.id,
          this.context
        );
        if (response.context_data) {
          this.context = { ...this.context, ...response.context_data };
          if (this.onContextUpdate) {
            this.onContextUpdate();
          }
        }
        return {
          message: response.message,
          isComplete: response.is_complete || false,
          extractedData: response.extracted_data
        };
      } else {
        if (!this.currentScenario) {
          return {
            message: 'Please select a scenario to begin.',
            isComplete: false
          };
        }
        const currentStep = this.currentScenario.steps[this.currentStep];
        if (!currentStep) {
          return {
            message: 'Conversation completed.',
            isComplete: true
          };
        }
        this.conversationHistory.push({
          sender: 'user',
          text: userInput,
          timestamp: new Date().toISOString()
        });
        const matchedResponse = this.matchResponse(userInput, currentStep.expectedResponses);
        if (!matchedResponse) {
          return {
            message: 'I didn\'t understand that. Could you please rephrase your response?',
            isComplete: false
          };
        }
        this.currentStep++;
        if (this.currentStep >= this.currentScenario.steps.length) {
          return {
            message: 'Thank you for your time. Have a great day!',
            isComplete: true
          };
        }
        const nextStep = this.currentScenario.steps[this.currentStep];
        const response = this.processMessage(nextStep.agent);
        this.conversationHistory.push({
          sender: 'agent',
          text: response,
          timestamp: new Date().toISOString()
        });
        return {
          message: response,
          stepId: nextStep.id,
          isComplete: false
        };
      }
    } catch (error) {
      console.error('Error processing user input:', error);
      this.useBackend = false;
      return this.processUserInput(userInput);
    } finally {
      this.setLoading(false);
    }
  }

  matchResponse(userInput, expectedResponses) {
    const input = userInput.toLowerCase().trim();
    for (const responseType of expectedResponses) {
      const mappings = responseMappings[responseType] || [responseType];
      for (const mapping of mappings) {
        if (input.includes(mapping.toLowerCase())) {
          return responseType;
        }
      }
    }
    return null;
  }

  processMessage(message) {
    return message
      .replace('{client_name}', this.context.clientName || this.context.client_name || 'Client')
      .replace('{phone_number}', this.context.phoneNumber || this.context.phone_number || '555-1234')
      .replace('{office_location}', this.context.officeLocation || this.context.office_location || 'Main Office')
      .replace('{office_state}', this.context.officeState || this.context.office_state || 'California')
      .replace('{adjusted_time}', this.context.adjustedTime || this.context.adjusted_time || '9:05')
      .replace('{adjusted_end_time}', this.context.adjustedEndTime || this.context.adjusted_end_time || '17:05')
      .replace('{clientName}', this.context.clientName || this.context.client_name || 'Client')
      .replace('{phoneNumber}', this.context.phoneNumber || this.context.phone_number || '555-1234')
      .replace('{officeLocation}', this.context.officeLocation || this.context.office_location || 'Main Office')
      .replace('{officeState}', this.context.officeState || this.context.office_state || 'California')
      .replace('{adjustedTime}', this.context.adjustedTime || this.context.adjusted_time || '9:05')
      .replace('{adjustedEndTime}', this.context.adjustedEndTime || this.context.adjusted_end_time || '17:05');
  }

  async getAvailableScenarios() {
    this.setLoading(true);
    try {
      if (this.useBackend) {
        const scenarios = await apiService.getScenarios();
        return scenarios;
      } else {
        return Object.values(scenarios);
      }
    } catch (error) {
      this.useBackend = false;
      return Object.values(scenarios);
    } finally {
      this.setLoading(false);
    }
  }

  getConversationHistory() {
    return [...this.conversationHistory];
  }

  async updateContext(newContext) {
    this.setLoading(true);
    const convertedContext = {};
    Object.entries(newContext).forEach(([key, value]) => {
      const contextKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
      convertedContext[contextKey] = value;
      convertedContext[key] = value;
    });
    this.context = { ...this.context, ...convertedContext };
    if (this.onContextUpdate) {
      this.onContextUpdate();
    }
    if (this.currentScenario && this.sessionId) {
      try {
        await apiService.updateContext(this.sessionId, convertedContext);
      } catch (error) {
        // ignore
      }
    }
    this.setLoading(false);
  }

  async checkBackendHealth() {
    this.setLoading(true);
    try {
      const isHealthy = await apiService.checkHealth();
      this.useBackend = isHealthy;
      return isHealthy;
    } catch (error) {
      this.useBackend = false;
      return false;
    } finally {
      this.setLoading(false);
    }
  }

  resetSession() {
    this.currentScenario = null;
    this.currentStep = 0;
    this.conversationHistory = [];
    this.context = {}; // Reset to completely empty context
    apiService.resetSession();
  }
} 