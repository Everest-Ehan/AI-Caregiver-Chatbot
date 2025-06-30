# AI Caregiver Chatbot

A comprehensive AI-powered chatbot system for caregiver call maintenance scenarios, featuring a modern frontend and intelligent LangGraph backend.

## 🚀 Features

- **🤖 Intelligent AI Agent**: LangGraph-powered conversation flow with state management
- **🎨 Modern UI**: Beautiful, responsive frontend with claymorphic design
- **🔄 Real-time Chat**: Seamless conversation experience with typing indicators
- **📊 Data Extraction**: Automatic extraction of structured data from conversations
- **🎯 Scenario-Based**: Different conversation flows for various caregiver issues
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🛡️ Fallback Support**: Graceful degradation when backend is unavailable

## 🏗️ Architecture

```
AI Caregiver Chatbot/
├── backend/                 # FastAPI + LangGraph backend
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration management
│   ├── run.py              # Startup script
│   ├── requirements.txt    # Python dependencies
│   └── agents/
│       └── caregiver_agent.py  # LangGraph agent
├── caregiver-chatbot/      # Vite + Vanilla JS frontend
│   ├── src/
│   │   ├── modules/        # UI components
│   │   ├── services/       # API integration
│   │   └── styles/         # CSS styling
│   └── package.json
└── start.bat              # Windows startup script
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (recommended) or Python 3.12 with pip
- **Node.js 16+** with npm
- **OpenAI API Key** (for AI functionality)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AI-Caregiver-Chatbot
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Install Python dependencies (Python 3.11 recommended)
python setup_python311.py

# Or manually:
# pip install -r requirements.txt

# Start backend server
python run.py
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd caregiver-chatbot

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### 4. Windows Quick Start

For Windows users, simply run:
```bash
start.bat
```

This will automatically start both backend and frontend servers.

## 📱 Usage

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Using the Chatbot

1. **Select Scenario**: Choose from available scenarios (Clock In, Clock Out, Schedule Conflict, GPS Location)
2. **Start Conversation**: The AI agent (Rosella) will greet you and guide the conversation
3. **Provide Information**: Answer questions one at a time as prompted
4. **Quick Responses**: Use the quick response buttons for common answers
5. **Context Data**: Fill in relevant context information in the right panel
6. **Completion**: The system will extract structured data when the conversation is complete

## 🔧 Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Model Configuration
MODEL_NAME=gpt-4o
MODEL_TEMPERATURE=0.4
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000`. To change the backend URL, edit `caregiver-chatbot/src/services/api.js`.

## 🤖 AI Agent Features

### LangGraph Workflow

1. **Issue Detection**: Automatically detects the type of issue from user input
2. **Contextual Responses**: Generates appropriate questions based on the selected scenario
3. **State Management**: Maintains conversation context and progress
4. **Data Extraction**: Extracts structured data when conversation completes

### Available Scenarios

- **Clock In Issue**: Help with clock in problems and schedule issues
- **Clock Out Issue**: Assist with clock out difficulties and time tracking
- **Schedule Conflict**: Resolve scheduling conflicts and availability issues
- **GPS Location Issue**: Help with GPS tracking and location verification

### Extracted Data

The system automatically extracts:
- Client name
- Caregiver name
- Issue type
- Resolution confirmation
- Additional notes and context

## 🎨 UI Features

### Design System

- **Claymorphic Design**: Soft, friendly interface with depth and shadows
- **Responsive Layout**: Three-panel layout that adapts to screen size
- **Smooth Animations**: CSS transitions and micro-interactions
- **Accessibility**: Keyboard navigation and screen reader support

### Components

- **Scenario Selector**: Expandable card-based scenario selection
- **Chat Interface**: Real-time messaging with typing indicators
- **Quick Responses**: Categorized quick response buttons
- **Context Panel**: Dynamic form fields based on selected scenario

## 🔌 API Integration

### Backend API Endpoints

- `POST /chat` - Process chat messages
- `GET /scenarios` - Get available scenarios
- `POST /start-session` - Start new chat session
- `GET /health` - Health check

### Frontend Integration

The frontend includes:
- **API Service**: Handles all backend communication
- **Fallback Support**: Graceful degradation when backend is unavailable
- **Error Handling**: User-friendly error messages
- **Session Management**: Persistent conversation state

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python run.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd caregiver-chatbot

# Start development server
npm run dev

# Build for production
npm run build
```

### Testing

```bash
# Test backend agent
cd backend
python -c "
from agents.caregiver_agent import create_caregiver_agent
from langchain.schema import HumanMessage

agent = create_caregiver_agent()
result = agent.invoke({
    'messages': [HumanMessage(content='Hi, I need help with clocking in')],
    'scenario_id': 'clock_in_issue'
})
print('Response:', result['messages'][-1].content)
"
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend Won't Start**
   - Check Python version (3.8+ required)
   - Verify OpenAI API key in `.env` file
   - Install dependencies: `pip install -r requirements.txt`

2. **Frontend Won't Connect**
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend
   - Verify API URL in `api.js`

3. **AI Not Responding**
   - Check OpenAI API key validity
   - Verify internet connection
   - Check API usage limits

4. **Import Errors**
   - Install missing dependencies
   - Check Python environment
   - Verify file paths

### Logs

- **Backend**: Check console output for detailed error messages
- **Frontend**: Open browser developer tools for JavaScript errors
- **API**: Monitor network requests in browser dev tools

## 📝 License

This project is part of the AI Caregiver Chatbot system.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Check console logs for error details 