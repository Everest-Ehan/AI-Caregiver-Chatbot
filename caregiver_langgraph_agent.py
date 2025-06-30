
from __future__ import annotations

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langchain.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, Optional
from datetime import datetime
import json

# ---- Define Shared State ----
from typing import Dict, Any

State = Dict[str, Any]

# ---- Load LLM ----
llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
parser = JsonOutputParser()
fmt = parser.get_format_instructions()

# ---- Prompts ----
system_prompt = """
<prompt>
<role>Your name is Rosella, a call center agent for Independence Care. Your task is to talk to caregivers and resolve clock-in, clock-out, and scheduling issues using the company guidelines. Ask these questions one at a time based on the situation.</role>
<constraints>
- If it's the first message, introduce yourself and start the conversation.
- Keep responses short, clear, and friendly.
- Ask only one question at a time.
- If you detect the issue has been resolved and all questions are answered, say "shift to end node".
- Use human-like conversational tone.
- Do not mention being an AI.
</constraints>
<purpose>{issue_type}</purpose>
<form_data>{form_data}</form_data>
</prompt>
"""

analysis_prompt = """
<prompt>
<role>Your job is to analyze the full chat with the caregiver and extract relevant information as JSON using the given output format.</role>
<output_format>{output_format}</output_format>
</prompt>
"""

output_schema = {
    "type": "object",
    "properties": {
        "client_name": {"type": "string", "description": "Name of the client"},
        "caregiver_name": {"type": "string", "description": "Name of the caregiver if mentioned"},
        "issue_type": {"type": "string", "enum": ["no_schedule", "late_clock_in", "gps_error", "ivr_error", "unregistered_phone", "duplicate_clock", "other"]},
        "confirmed_resolution": {"type": "boolean", "description": "Whether the issue was resolved and confirmed with the client"},
        "notes": {"type": "string"}
    },
    "required": ["client_name", "issue_type", "confirmed_resolution"]
}

# ---- Functions ----
def detect_issue_type(state: State):
    last_input = state["messages"][-1].content.lower()
    if "no schedule" in last_input:
        issue = "no_schedule"
    elif "late" in last_input:
        issue = "late_clock_in"
    elif "gps" in last_input or "location" in last_input:
        issue = "gps_error"
    elif "ivr" in last_input or "call" in last_input:
        issue = "ivr_error"
    elif "not registered" in last_input or "new phone" in last_input:
        issue = "unregistered_phone"
    elif "duplicate" in last_input:
        issue = "duplicate_clock"
    else:
        issue = "other"
    return {**state, "issue_type": issue}

def get_system_prompt(state: State):
    tmpl = PromptTemplate.from_template(system_prompt)
    formatted = tmpl.format(issue_type=state["issue_type"], form_data=state.get("form_data", {}))
    return SystemMessage(content=formatted)

def ask_question(state: State):
    response = llm.invoke([get_system_prompt(state), *state["messages"]])
    return {**state, "messages": [*state["messages"], response]}

def analyse_chat(state: State):
    schema_str = json.dumps(output_schema, indent=2)
    prompt = PromptTemplate.from_template(analysis_prompt)
    formatted = prompt.format(output_format=schema_str)
    response = llm.invoke([SystemMessage(content=formatted), *state["messages"]])
    return {**state, "result": parser.parse(response.content)}

def router(state: State):
    if "shift to end node" in state["messages"][-1].content.lower():
        return "analyse_chat"
    else:
        return "ask_question"

# ---- Build LangGraph ----
graph = (
    StateGraph(State)
    .add_node("detect_issue", detect_issue_type)
    .add_node("ask_question", ask_question)
    .add_node("analyse_chat", analyse_chat)
    .add_conditional_edges("ask_question", router, {"ask_question": "ask_question", "analyse_chat": "analyse_chat"})
    .add_edge(START, "detect_issue")
    .add_edge("detect_issue", "ask_question")
    .add_edge("analyse_chat", END)
    .compile(checkpointer=MemorySaver())
)

# ---- Example run ----
if __name__ == "__main__":
    result = graph.invoke({
        "messages": [
            HumanMessage(content="Hi, I clocked in but the schedule is missing on the calendar")
        ],
        "form_data": {},
    })

    for msg in result["messages"]:
        print("Rosella:" if isinstance(msg, SystemMessage) else "Caregiver:", msg.content)

    print("\nExtracted Result:")
    print(result["result"])
