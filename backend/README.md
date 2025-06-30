# Caregiver Chatbot Backend

A FastAPI backend with LangGraph integration for AI-powered caregiver call maintenance scenarios.

## Features

- 🤖 **LangGraph Agent**: Intelligent conversation flow with state management
- 🔄 **Session Management**: Persistent chat sessions with context
- 📊 **Structured Data Extraction**: Automatic extraction of relevant information
- 🎯 **Scenario-Based**: Different conversation flows for various caregiver issues
- 🔧 **RESTful API**: Clean API endpoints for frontend integration

## Quick Start

### Prerequisites
- **Python 3.11** (recommended) or Python 3.12
- **OpenAI API Key** for AI functionality

### 1. Install Dependencies

**For Python 3.11 (Recommended):**
```bash
# Run the setup script for Python 3.11 compatibility
python setup_python311.py
```

**Manual installation:**
```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the backend directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 3. Start the Server

```bash
# Option 1: Using the startup script
python run.py

# Option 2: Direct uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/

## API Endpoints

### Chat Endpoints

#### `POST /chat`
Process a chat message and return the agent's response.

**Request Body:**
```json
{
  "message": "Hi, I'm having trouble clocking in",
  "scenario_id": "clock_in_issue",
  "context_data": {
    "client_name": "John Smith"
  },
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "message": "Hello! I'm Rosella from Independence Care. I can help you with your clock-in issue. Could you please tell me your name?",
  "session_id": "session_abc123",
  "is_complete": false,
  "extracted_data": null
}
```

#### `GET /scenarios`
Get available scenarios for the chatbot.

**Response:**
```json
[
  {
    "id": "clock_in_issue",
    "name": "Clock In Issue",
    "description": "Help with clock in problems and schedule issues",
    "context_fields": ["client_name", "caregiver_name", "clock_in_time", "location"]
  }
]
```

#### `POST /start-session`
Start a new chat session with a specific scenario.

**Query Parameters:**
- `scenario_id`: The scenario to start with

## LangGraph Agent

The backend uses LangGraph to create intelligent conversation flows:

### State Management
- **Messages**: Conversation history
- **Issue Type**: Detected issue category
- **Session ID**: Unique session identifier
- **Scenario ID**: Current scenario context
- **Context Data**: Additional context information

### Conversation Flow
1. **Issue Detection**: Automatically detect issue type from user input
2. **Question Generation**: Generate contextual questions based on scenario
3. **Response Processing**: Process user responses and maintain context
4. **Data Extraction**: Extract structured data when conversation completes

### Available Scenarios
- **Clock In Issue**: Help with clock in problems and schedule issues
- **Clock Out Issue**: Assist with clock out difficulties and time tracking
- **Schedule Conflict**: Resolve scheduling conflicts and availability issues
- **GPS Location Issue**: Help with GPS tracking and location verification

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── run.py               # Startup script
├── requirements.txt     # Python dependencies
├── agents/
│   ├── __init__.py
│   └── caregiver_agent.py  # LangGraph agent implementation
└── README.md
```

### Adding New Scenarios

1. Update the scenarios list in `main.py`
2. Add scenario-specific prompts in `agents/caregiver_agent.py`
3. Update the issue detection logic if needed

### Testing

Test the agent directly:

```bash
cd backend
python -c "
from agents.caregiver_agent import create_caregiver_agent
from langchain.schema import HumanMessage

agent = create_caregiver_agent()
result = agent.invoke({
    'messages': [HumanMessage(content='Hi, I need help with clocking in')],
    'scenario_id': 'clock_in_issue'
})

print('Agent Response:', result['messages'][-1].content)
"
```

## Integration with Frontend

The backend is designed to work with the Vite frontend:

1. **CORS**: Configured to allow requests from `http://localhost:5173`
2. **Session Management**: Maintains conversation state across requests
3. **Real-time Chat**: Supports streaming responses for better UX

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

3. **CORS Issues**
   - Check that your frontend URL is in `ALLOWED_ORIGINS`

4. **Agent Not Initializing**
   - Check OpenAI API key and network connectivity
   - Verify model name in configuration

### Logs

The server provides detailed logs for debugging:
- Agent initialization status
- Request/response logging
- Error details with stack traces

## License

This project is part of the AI Caregiver Chatbot system. 