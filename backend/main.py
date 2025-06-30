from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json

# Import our configuration and agent
from config import Config
from agents.caregiver_agent import create_caregiver_agent

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please create a .env file with your OpenAI API key")
    exit(1)

app = FastAPI(
    title="Caregiver Chatbot API",
    description="AI-powered caregiver call maintenance system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LangGraph agent
try:
    caregiver_agent = create_caregiver_agent()
    if caregiver_agent is None:
        print("❌ LangGraph agent creation returned None")
        caregiver_agent = None
    else:
        print("✅ LangGraph agent initialized successfully")
except Exception as e:
    print(f"❌ Error initializing LangGraph agent: {e}")
    import traceback
    traceback.print_exc()
    caregiver_agent = None

# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    scenario_id: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    is_complete: bool = False
    extracted_data: Optional[Dict[str, Any]] = None

class ScenarioInfo(BaseModel):
    id: str
    name: str
    description: str
    context_fields: List[str]

# API Routes
@app.get("/")
async def root():
    return {"message": "Caregiver Chatbot API is running"}

@app.get("/health")
async def health_check():
    agent_status = "ready" if caregiver_agent else "error"
    return {"status": "healthy", "agent": agent_status}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return the AI's response
    """
    try:
        # Simple AI responses based on user input
        user_message = request.message.lower()
        
        # Basic conversation patterns
        if any(word in user_message for word in ["hello", "hi", "hey"]):
            message = "Hello! How can I help you today?"
        elif any(word in user_message for word in ["how are you", "how do you do"]):
            message = "I'm doing well, thank you for asking! How about you?"
        elif any(word in user_message for word in ["bye", "goodbye", "see you"]):
            message = "Goodbye! Have a great day!"
        elif any(word in user_message for word in ["thank you", "thanks"]):
            message = "You're welcome! Is there anything else I can help you with?"
        elif any(word in user_message for word in ["what can you do", "help", "what do you do"]):
            message = "I'm a simple AI assistant. I can chat with you, answer questions, and help with basic tasks. What would you like to talk about?"
        elif any(word in user_message for word in ["weather", "temperature"]):
            message = "I can't check the weather right now, but I hope it's nice where you are!"
        elif any(word in user_message for word in ["name", "who are you"]):
            message = "I'm an AI assistant created to help with conversations. What's your name?"
        elif "?" in user_message:
            message = "That's an interesting question! I'm still learning, but I'd love to hear more about what you're thinking."
        else:
            # Echo back with some variation
            message = f"I understand you said: '{request.message}'. Tell me more about that!"
        
        return ChatResponse(
            message=message,
            session_id=request.session_id or "default",
            is_complete=False,
            extracted_data=None
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/scenarios", response_model=List[ScenarioInfo])
async def get_scenarios():
    """
    Get available scenarios for the chatbot
    """
    scenarios = [
        ScenarioInfo(
            id="clock_in_issue",
            name="Clock In Issue",
            description="Help with clock in problems and schedule issues",
            context_fields=["client_name", "caregiver_name", "clock_in_time", "location"]
        ),
        ScenarioInfo(
            id="clock_out_issue", 
            name="Clock Out Issue",
            description="Assist with clock out difficulties and time tracking",
            context_fields=["client_name", "caregiver_name", "clock_out_time", "hours_worked"]
        ),
        ScenarioInfo(
            id="schedule_conflict",
            name="Schedule Conflict",
            description="Resolve scheduling conflicts and availability issues",
            context_fields=["client_name", "caregiver_name", "conflict_date", "availability"]
        ),
        ScenarioInfo(
            id="gps_location",
            name="GPS Location Issue",
            description="Help with GPS tracking and location verification",
            context_fields=["client_name", "caregiver_name", "location", "gps_status"]
        )
    ]
    return scenarios

class StartSessionRequest(BaseModel):
    scenario_id: str

@app.post("/start-session")
async def start_session(request: StartSessionRequest):
    """
    Start a new chat session with a specific scenario
    """
    try:
        # Initialize a new session with the selected scenario
        initial_state = {
            "messages": [],
            "session_id": f"session_{os.urandom(8).hex()}",
            "scenario_id": request.scenario_id,
            "context_data": {}
        }
        
        # You could store this in a session store here
        return {
            "session_id": initial_state["session_id"],
            "scenario_id": request.scenario_id,
            "message": "Session started successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT,
        reload=Config.DEBUG
    ) 