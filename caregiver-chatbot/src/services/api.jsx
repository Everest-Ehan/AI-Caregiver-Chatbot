/**
 * API Service for communicating with the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.sessionId = null;
  }

  /**
   * Make a request to the API
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const requestOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  /**
   * Get available scenarios from the backend
   */
  async getScenarios() {
    try {
      const scenarios = await this.makeRequest('/scenarios');
      return scenarios;
    } catch (error) {
      console.error('Failed to fetch scenarios:', error);
      // Return fallback scenarios if API is unavailable
      return [
        {
          id: "clock_in_issue",
          name: "Clock In Issue",
          description: "Help with clock in problems and schedule issues",
          context_fields: ["client_name", "caregiver_name", "clock_in_time", "location"]
        },
        {
          id: "clock_out_issue",
          name: "Clock Out Issue", 
          description: "Assist with clock out difficulties and time tracking",
          context_fields: ["client_name", "caregiver_name", "clock_out_time", "hours_worked"]
        },
        {
          id: "schedule_conflict",
          name: "Schedule Conflict",
          description: "Resolve scheduling conflicts and availability issues",
          context_fields: ["client_name", "caregiver_name", "conflict_date", "availability"]
        },
        {
          id: "gps_location",
          name: "GPS Location Issue",
          description: "Help with GPS tracking and location verification",
          context_fields: ["client_name", "caregiver_name", "location", "gps_status"]
        }
      ];
    }
  }

  /**
   * Start a new chat session
   */
  async startSession(scenarioId) {
    try {
      const response = await this.makeRequest('/start-session', {
        method: 'POST',
        body: JSON.stringify({ scenario_id: scenarioId }),
      });
      
      this.sessionId = response.session_id;
      return response;
    } catch (error) {
      console.error('Failed to start session:', error);
      // Generate a fallback session ID
      this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      return {
        session_id: this.sessionId,
        scenario_id: scenarioId,
        message: "Session started (offline mode)"
      };
    }
  }

  /**
   * Send a chat message to the backend
   */
  async sendMessage(message, scenarioId = null, contextData = {}) {
    try {
      const requestBody = {
        message,
        scenario_id: scenarioId,
        context_data: contextData,
        session_id: this.sessionId,
      };

      const response = await this.makeRequest('/chat', {
        method: 'POST',
        body: JSON.stringify(requestBody),
      });

      // Update session ID if provided
      if (response.session_id) {
        this.sessionId = response.session_id;
      }

      return response;
    } catch (error) {
      console.error('Failed to send message:', error);
      // Return a fallback response
      return {
        message: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later.",
        session_id: this.sessionId,
        is_complete: false,
        extracted_data: null
      };
    }
  }

  /**
   * Check if the backend is available
   */
  async checkHealth() {
    try {
      const response = await this.makeRequest('/health');
      return response.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Get the current session ID
   */
  getSessionId() {
    return this.sessionId;
  }

  /**
   * Update context data for the current session
   */
  async updateContext(sessionId, contextData) {
    try {
      const response = await this.makeRequest('/update-context', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          context_data: contextData
        }),
      });
      
      return response;
    } catch (error) {
      console.error('Failed to update context:', error);
      throw error;
    }
  }

  /**
   * Reset session context data completely
   */
  async resetSessionContext(sessionId, contextData) {
    try {
      const response = await this.makeRequest('/reset-session-context', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          context_data: contextData
        }),
      });
      
      return response;
    } catch (error) {
      console.error('Failed to reset session context:', error);
      throw error;
    }
  }

  /**
   * Reset the session
   */
  resetSession() {
    this.sessionId = null;
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService; 