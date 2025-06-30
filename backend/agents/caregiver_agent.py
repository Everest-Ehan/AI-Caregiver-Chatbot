# backend/caregiver_agent.py

from langgraph.graph import StateGraph
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai.chat_models import ChatOpenAI
from typing import TypedDict, Annotated

class ChatState(TypedDict):
    messages: list
    scenario_id: str
    context_data: dict

llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

def get_scenario_prompt(scenario_id: str) -> str:
    """Get scenario-specific system prompt"""
    prompts = {
        "general_chat": "You are a helpful and friendly AI assistant. Be conversational and helpful.",
        "no_schedule": """You are Rosella from Independence Care, a professional caregiver support representative. 
        You're helping a caregiver who clocked in but has no schedule showing on their calendar. 
        Be professional, empathetic, and guide them through resolving this issue. 
        Ask for client name, caregiver name, regular schedule, and office location as needed.""",
        "out_of_window": """You are Rosella from Independence Care, a professional caregiver support representative. 
        You're helping a caregiver who clocked in late for their shift. 
        Be professional, understanding, and help them adjust their schedule properly. 
        Ask for client name, caregiver name, scheduled start time, actual start time, shift duration, office location, and reason for being late as needed.""",
        "gps_out_of_range": """You are Rosella from Independence Care, a professional caregiver support representative. 
        You're helping a caregiver who clocked in outside the client's service area. 
        Be professional, firm but understanding, and guide them to clock in properly. 
        Ask for client name, caregiver name, client address, clock-in location, office state, and errand details if applicable.""",
        "wrong_phone": """You are Rosella from Independence Care, a professional caregiver support representative. 
        You're helping a caregiver who used the IVR number from their phone instead of the client's house phone. 
        Be professional, clear about the policy, and guide them to use the correct phone. 
        Ask for client name, caregiver name, client phone, caregiver phone, and IVR number used.""",
        "phone_not_found": """You are Rosella from Independence Care, a professional caregiver support representative. 
        You're helping a caregiver who used an unregistered phone number to clock in. 
        Be professional, verify the phone number ownership, and help update their profile. 
        Ask for client name, caregiver name, new phone number, old phone number, and phone owner."""
    }
    return prompts.get(scenario_id, prompts["general_chat"])

def generate_reply(state: ChatState):
    # Check if there are any messages
    if not state["messages"]:
        scenario_id = state.get("scenario_id", "general_chat")
        system_prompt = get_scenario_prompt(scenario_id)
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Hello, I need help with my issue")
        ])
        return {"messages": [response]}
    
    # Get the content from the last message
    last_message = state["messages"][-1]
    if hasattr(last_message, 'content'):
        message_content = last_message.content
    else:
        message_content = str(last_message)
    
    # Get scenario-specific prompt
    scenario_id = state.get("scenario_id", "general_chat")
    system_prompt = get_scenario_prompt(scenario_id)
    
    # Create conversation with system prompt
    conversation = [SystemMessage(content=system_prompt)]
    
    # Add context data if available
    context_data = state.get("context_data", {})
    if context_data:
        context_str = "Context information: " + ", ".join([f"{k}: {v}" for k, v in context_data.items() if v])
        if context_str != "Context information: ":
            conversation.append(HumanMessage(content=context_str))
    
    # Add the user's message
    conversation.append(HumanMessage(content=message_content))
    
    response = llm.invoke(conversation)
    return {"messages": state["messages"] + [response]}

builder = StateGraph(ChatState)
builder.add_node("generate_reply", generate_reply)
builder.set_entry_point("generate_reply")
builder.set_finish_point("generate_reply")
chat_graph = builder.compile()

