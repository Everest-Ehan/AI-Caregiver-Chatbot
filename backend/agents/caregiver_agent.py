from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, Optional, Dict, Any
from datetime import datetime
import json
import os

# ---- Define Shared State ----
class State(TypedDict):
    messages: Annotated[list, add_messages]
    issue_type: Optional[str]
    form_data: Optional[dict]
    result: Optional[dict]
    session_id: Optional[str]
    scenario_id: Optional[str]
    context_data: Optional[dict]
    is_complete: Optional[bool]

# ---- Load LLM ----
llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY")
)
parser = JsonOutputParser()
fmt = parser.get_format_instructions()

# ---- Prompts ----
system_prompt = """
You are Rosella, a call center agent for Independence Care. Your task is to talk to caregivers and resolve clock-in, clock-out, and scheduling issues using the company guidelines.

Current Scenario: {scenario_id}
Context Data: {context_data}

Guidelines:
- Keep responses short, clear, and friendly
- Ask only one question at a time
- Use human-like conversational tone
- Do not mention being an AI
- If the issue has been resolved and all necessary information is collected, say "CONVERSATION_COMPLETE"
- Focus on gathering: client name, caregiver name, specific issue details, and resolution confirmation

Available scenarios:
- clock_in_issue: Help with clock in problems and schedule issues
- clock_out_issue: Assist with clock out difficulties and time tracking  
- schedule_conflict: Resolve scheduling conflicts and availability issues
- gps_location: Help with GPS tracking and location verification

Previous messages: {message_history}
"""

analysis_prompt = """
Analyze the full conversation with the caregiver and extract relevant information as JSON using the given output format.

Conversation: {conversation}

Output Format:
{output_format}
"""

output_schema = {
    "type": "object",
    "properties": {
        "client_name": {"type": "string", "description": "Name of the client"},
        "caregiver_name": {"type": "string", "description": "Name of the caregiver if mentioned"},
        "issue_type": {"type": "string", "enum": ["clock_in_issue", "clock_out_issue", "schedule_conflict", "gps_location", "other"]},
        "confirmed_resolution": {"type": "boolean", "description": "Whether the issue was resolved and confirmed"},
        "notes": {"type": "string", "description": "Additional notes about the conversation"},
        "extracted_data": {"type": "object", "description": "Any additional data extracted from the conversation"}
    },
    "required": ["client_name", "issue_type", "confirmed_resolution"]
}

# ---- Functions ----
def detect_issue_type(state: State):
    """Detect the type of issue from the user's message"""
    if not state.get("messages"):
        return state
    
    last_message = state["messages"][-1]
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        
        if any(word in content for word in ["clock in", "clockin", "start work", "begin shift"]):
            issue = "clock_in_issue"
        elif any(word in content for word in ["clock out", "clockout", "end work", "finish shift"]):
            issue = "clock_out_issue"
        elif any(word in content for word in ["schedule", "conflict", "availability", "time off"]):
            issue = "schedule_conflict"
        elif any(word in content for word in ["gps", "location", "tracking", "where"]):
            issue = "gps_location"
        else:
            issue = "other"
            
        return {**state, "issue_type": issue}
    
    return state

def get_system_prompt(state: State):
    """Generate the system prompt based on current state"""
    scenario_id = state.get("scenario_id", "general")
    context_data = state.get("context_data", {})
    
    # Build message history
    message_history = ""
    if state.get("messages"):
        for msg in state["messages"][-5:]:  # Last 5 messages for context
            if isinstance(msg, HumanMessage):
                message_history += f"Caregiver: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                message_history += f"Rosella: {msg.content}\n"
    
    tmpl = PromptTemplate.from_template(system_prompt)
    formatted = tmpl.format(
        scenario_id=scenario_id,
        context_data=json.dumps(context_data, indent=2),
        message_history=message_history
    )
    return SystemMessage(content=formatted)

def ask_question(state: State):
    """Generate the next question/response from the agent"""
    try:
        # Get system prompt
        system_msg = get_system_prompt(state)
        
        # Get conversation history
        conversation_messages = [system_msg]
        if state.get("messages"):
            conversation_messages.extend(state["messages"])
        
        # Generate response
        response = llm.invoke(conversation_messages)
        
        # Check if conversation is complete
        is_complete = "CONVERSATION_COMPLETE" in response.content
        
        return {
            **state, 
            "messages": [*state["messages"], response],
            "is_complete": is_complete
        }
        
    except Exception as e:
        # Fallback response
        fallback_response = AIMessage(content="I'm sorry, I'm having trouble processing that. Could you please repeat your question?")
        return {
            **state,
            "messages": [*state["messages"], fallback_response],
            "is_complete": False
        }

def analyse_chat(state: State):
    """Analyze the conversation and extract structured data"""
    try:
        # Build conversation text
        conversation = ""
        if state.get("messages"):
            for msg in state["messages"]:
                if isinstance(msg, HumanMessage):
                    conversation += f"Caregiver: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    conversation += f"Rosella: {msg.content}\n"
        
        # Generate analysis prompt
        schema_str = json.dumps(output_schema, indent=2)
        prompt = PromptTemplate.from_template(analysis_prompt)
        formatted = prompt.format(
            conversation=conversation,
            output_format=schema_str
        )
        
        # Get analysis
        response = llm.invoke([SystemMessage(content=formatted)])
        parsed_result = parser.parse(response.content)
        
        return {
            **state,
            "result": parsed_result,
            "is_complete": True
        }
        
    except Exception as e:
        # Fallback result
        fallback_result = {
            "client_name": "Unknown",
            "caregiver_name": "Unknown", 
            "issue_type": state.get("issue_type", "other"),
            "confirmed_resolution": False,
            "notes": f"Error in analysis: {str(e)}",
            "extracted_data": {}
        }
        
        return {
            **state,
            "result": fallback_result,
            "is_complete": True
        }

def router(state: State):
    """Route to next node based on conversation state"""
    if state.get("is_complete", False):
        return "analyse_chat"
    else:
        return "ask_question"

# ---- Build LangGraph ----
def create_caregiver_agent():
    """Create and return the LangGraph agent"""
    try:
        # 1. First, instantiate the graph
        workflow = StateGraph(State)

        # 2. Then, add the nodes
        workflow.add_node("detect_issue", detect_issue_type)
        workflow.add_node("ask_question", ask_question)
        workflow.add_node("analyse_chat", analyse_chat)

        # 3. Define the entry point and edges
        workflow.set_entry_point("detect_issue")
        workflow.add_edge("detect_issue", "ask_question")
        workflow.add_edge("analyse_chat", END)
        
        # 4. Add the conditional edge for routing
        workflow.add_conditional_edges(
            "ask_question",
            router,
            {
                "ask_question": "ask_question",
                "analyse_chat": "analyse_chat",
            }
        )

        # 5. Finally, compile the graph
        graph = workflow.compile(checkpointer=MemorySaver())
        
        return graph
    except Exception as e:
        print(f"Error creating LangGraph agent: {e}")
        import traceback
        traceback.print_exc()
        return None
# ---- Example usage ----
if __name__ == "__main__":
    # Test the agent
    agent = create_caregiver_agent()
    
    result = agent.invoke({
        "messages": [
            HumanMessage(content="Hi, I'm having trouble clocking in for my shift")
        ],
        "scenario_id": "clock_in_issue",
        "context_data": {"client_name": "John Smith"},
        "session_id": "test_session"
    })

    print("Conversation:")
    for msg in result["messages"]:
        if isinstance(msg, HumanMessage):
            print(f"Caregiver: {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"Rosella: {msg.content}")

    print("\nExtracted Result:")
    print(json.dumps(result.get("result", {}), indent=2)) 