# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from uuid import uuid4
from agents.caregiver_agent import chat_graph
from langchain_core.messages import HumanMessage, AIMessage

# In-memory session storage
sessions = {}

app = FastAPI()

# Allow all origins (in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartSessionRequest(BaseModel):
    scenario_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: str
    scenario_id: Optional[str] = None
    context_data: Optional[Dict] = {}

class UpdateContextRequest(BaseModel):
    session_id: str
    context_data: Dict[str, str]

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/scenarios")
def get_scenarios():
    print("getting scenarios")
    return [
        {"id": "general_chat", "name": "General Chat", "description": "Test generic conversation", "context_fields": []},
        {
            "id": "no_schedule",
            "name": "No Schedule on Calendar",
            "description": "Caregiver clocked in but no schedule appears on calendar",
            "context_fields": ["client_name", "caregiver_name", "regular_schedule", "office_location"]
        },
        {
            "id": "out_of_window",
            "name": "Out of Window (Late Clock In)",
            "description": "Caregiver clocked in late for their shift",
            "context_fields": ["client_name", "caregiver_name", "scheduled_start_time", "actual_start_time", "shift_duration", "office_location", "late_reason"]
        },
        {
            "id": "gps_out_of_range",
            "name": "GPS Signal Out of Range",
            "description": "Caregiver clocked in outside client's service area",
            "context_fields": ["client_name", "caregiver_name", "client_address", "clock_in_location", "office_state", "errand_details"]
        },
        {
            "id": "wrong_phone",
            "name": "Call From Caregiver Number",
            "description": "Caregiver used IVR number from their phone instead of client's house phone",
            "context_fields": ["client_name", "caregiver_name", "client_phone", "caregiver_phone", "ivr_number"]
        },
        {
            "id": "phone_not_found",
            "name": "Phone Number Not Found",
            "description": "Caregiver used unregistered phone number",
            "context_fields": ["client_name", "caregiver_name", "new_phone_number", "old_phone_number", "phone_owner"]
        },
        {
            "id": "duplicate_call",
            "name": "Duplicate Call",
            "description": "Caregiver accidentally clocked in or out more than once; no call needed, call will be rejected.",
            "context_fields": []
        }
    ]

@app.post("/start-session")
def start_session(data: StartSessionRequest):
    session_id = f"session_{uuid4().hex}"
    sessions[session_id] = {
        "messages": [],
        "scenario_id": data.scenario_id,
        "context_data": {},
    }
    
    # Get scenario info for the response
    scenario_info = {
        "id": data.scenario_id,
        "name": "General Chat" if data.scenario_id == "general_chat" else "Caregiver Support",
        "description": "Professional assistance for caregiver issues"
    }
    
    return {
        "session_id": session_id, 
        "scenario_id": data.scenario_id, 
        "message": f"Session started for {scenario_info['name']}"
    }

@app.post("/chat")
def chat(request: ChatRequest):
    session = sessions.get(request.session_id)
    if not session:
        return {"message": "Invalid session", "is_complete": True}

    # Update scenario_id if provided in the request
    if request.scenario_id:
        session["scenario_id"] = request.scenario_id

    # Merge all incoming context fields into session context (no filtering)
    if request.context_data:
        session["context_data"].update(request.context_data)

    # Add user message as LangChain HumanMessage
    human_message = HumanMessage(content=request.message)
    session["messages"].append(human_message)

    # Prepare state for LangGraph
    state = {
        "messages": session["messages"],
        "scenario_id": session.get("scenario_id", "general_chat"),
        "context_data": session.get("context_data", {})
    }

    result = chat_graph.invoke(state, config={"thread_id": request.session_id})

    # Extract bot message from the result
    if "messages" in result and result["messages"]:
        # Get the last message which should be the AI response
        last_message = result["messages"][-1]
        if hasattr(last_message, 'content'):
            bot_response = last_message.content
        else:
            bot_response = str(last_message)
    else:
        bot_response = "I didn't get that."

    # Extract and update context_data from the result
    context_data = result.get("context_data", {})
    if context_data:
        session["context_data"].update(context_data)

    # Append bot response to history
    ai_message = AIMessage(content=bot_response)
    session["messages"].append(ai_message)

    # Always return the full context_data
    return {
        "message": bot_response,
        "session_id": request.session_id,
        "is_complete": False,
        "extracted_data": None,
        "context_data": session["context_data"],  # Return the updated context_data
    }

@app.post("/update-context")
def update_context(request: UpdateContextRequest):
    session = sessions.get(request.session_id)
    if not session:
        return {"error": "Invalid session"}
    
    # Update context data
    session["context_data"].update(request.context_data)
    
    return {
        "session_id": request.session_id,
        "context_data": session["context_data"],
        "message": "Context updated successfully"
    }