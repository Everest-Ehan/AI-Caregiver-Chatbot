import { scenarios, responseMappings } from '../data/scenarios.js';
import apiService from '../services/api.js';

export default class ChatbotEngine {
  constructor() {
    this.currentScenario = null;
    this.currentStep = 0;
    this.conversationHistory = [];
    this.context = {
      clientName: 'John Doe',
      phoneNumber: '555-1234',
      officeLocation: 'Main Office',
      officeState: 'California',
      adjustedTime: '9:05',
      adjustedEndTime: '17:05'
    };
    this.useBackend = true; // Flag to control backend vs frontend processing
  }

  async startScenario(scenarioId) {
    try {
      if (this.useBackend) {
        // Use backend API
        const sessionResponse = await apiService.startSession(scenarioId);
        
        // Store session ID
        this.sessionId = sessionResponse.session_id;
        
        // Get scenarios from backend to find the selected one
        const scenarios = await apiService.getScenarios();
        const scenario = scenarios.find(s => s.id === scenarioId);
        
        if (scenario) {
          this.currentScenario = scenario;
        }
        
        // Send initial message to start conversation
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
        // Fallback to frontend processing
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
      // Fallback to frontend processing
      this.useBackend = false;
      return this.startScenario(scenarioId);
    }
  }

  getCurrentScenarioContextFields() {
    console.log('getCurrentScenarioContextFields called');
    console.log('Current scenario:', this.currentScenario);
    console.log('Use backend:', this.useBackend);
    
    if (!this.currentScenario) {
      console.log('No current scenario, returning empty object');
      return {};
    }
    
    if (this.useBackend && this.currentScenario.context_fields) {
      console.log('Using backend context fields:', this.currentScenario.context_fields);
      // Convert backend context fields to frontend format
      const contextFields = {};
      this.currentScenario.context_fields.forEach(field => {
        contextFields[field] = {
          label: field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          placeholder: `Enter ${field.replace(/_/g, ' ').toLowerCase()}`,
          type: 'text',
          required: false
        };
      });
      console.log('Converted context fields:', contextFields);
      return contextFields;
    }
    
    console.log('Using frontend context fields:', this.currentScenario.contextFields);
    return this.currentScenario.contextFields || {};
  }

  getCurrentScenario() {
    return this.currentScenario;
  }

  async processUserInput(userInput) {
    try {
      if (this.useBackend) {
        // Use backend API
        const response = await apiService.sendMessage(
          userInput,
          this.currentScenario?.id,
          this.context
        );
        
        return {
          message: response.message,
          isComplete: response.is_complete || false,
          extractedData: response.extracted_data
        };
      } else {
        // Fallback to frontend processing
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

        // Add user message to history
        this.conversationHistory.push({
          sender: 'user',
          text: userInput,
          timestamp: new Date().toISOString()
        });

        // Check if user input matches expected responses
        const matchedResponse = this.matchResponse(userInput, currentStep.expectedResponses);
        
        if (!matchedResponse) {
          // If no match, ask for clarification
          return {
            message: 'I didn\'t understand that. Could you please rephrase your response?',
            isComplete: false
          };
        }

        // Move to next step
        this.currentStep++;

        // Check if conversation is complete
        if (this.currentStep >= this.currentScenario.steps.length) {
          return {
            message: 'Thank you for your time. Have a great day!',
            isComplete: true
          };
        }

        // Get next step
        const nextStep = this.currentScenario.steps[this.currentStep];
        const response = this.processMessage(nextStep.agent);

        // Add agent message to history
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
      // Fallback to frontend processing
      this.useBackend = false;
      return this.processUserInput(userInput);
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
    // Replace placeholders with context values
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
    try {
      if (this.useBackend) {
        // Get scenarios from backend
        const scenarios = await apiService.getScenarios();
        return scenarios.map(scenario => ({
          id: scenario.id,
          name: scenario.name,
          description: scenario.description
        }));
      } else {
        // Fallback to frontend scenarios
        return Object.values(scenarios).map(scenario => ({
          id: scenario.id,
          name: scenario.name,
          description: scenario.description
        }));
      }
    } catch (error) {
      console.error('Error getting scenarios:', error);
      // Fallback to frontend scenarios
      this.useBackend = false;
      return Object.values(scenarios).map(scenario => ({
        id: scenario.id,
        name: scenario.name,
        description: scenario.description
      }));
    }
  }

  getConversationHistory() {
    return [...this.conversationHistory];
  }

  async updateContext(newContext) {
    // Convert field keys to context keys and merge
    const convertedContext = {};
    Object.entries(newContext).forEach(([key, value]) => {
      // Handle both camelCase and snake_case keys
      const contextKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
      convertedContext[contextKey] = value;
      // Also keep original key for backward compatibility
      convertedContext[key] = value;
    });
    
    this.context = { ...this.context, ...convertedContext };
    
    // Send context update to backend if we have a session
    if (this.currentScenario && this.sessionId) {
      try {
        await apiService.updateContext(this.sessionId, convertedContext);
      } catch (error) {
        console.error('Error updating context on backend:', error);
      }
    }
  }

  async checkBackendHealth() {
    try {
      const isHealthy = await apiService.checkHealth();
      this.useBackend = isHealthy;
      return isHealthy;
    } catch (error) {
      console.error('Backend health check failed:', error);
      this.useBackend = false;
      return false;
    }
  }

  resetSession() {
    this.currentScenario = null;
    this.currentStep = 0;
    this.conversationHistory = [];
    apiService.resetSession();
  }
} 