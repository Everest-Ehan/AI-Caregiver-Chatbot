from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

def general_chat_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    context_fields = [
        "caregiver_name",
        "client_name",
        "general_chat_topic",
        "substep"
    ]
    workflow = [
        {"substep": "greet", "description": "Greet and start general conversation.", "extract": []},
        {"substep": "conversation", "description": "Handle general chat and support.", "extract": ["general_chat_topic"]},
        {"substep": "end", "description": "End the conversation politely.", "extract": []},
    ]
    scenario_examples = """
Example 1:
Caregiver: I need help with my schedule.
Agent: Sure, what do you need help with regarding your schedule?

Example 2:
Caregiver: Can you tell me how to use the app?
Agent: Of course! What would you like to know about the app?
"""
    system_prompt = (
        f"You are Rosella from Independence Care, a professional caregiver support representative.\n"
        f"Your main job is to extract and update all relevant context fields for this scenario after each message.\n"
        f"Extraction rules (ALWAYS follow):\n"
        f"- After every message, extract and update ALL context fields you can infer from the conversation so far, even if not explicitly stated.\n"
        f"- Always make sense of the conversation as a whole.\n"
        f"- If a field is already present and valid, do not ask for it again.\n"
        f"- Only ask for missing or unclear information.\n"
        f"- If the workflow is complete, set 'substep' to 'end'.\n"
        f"- If you need more information, keep the substep the same and ask for clarification.\n"
        f"- Never break, always handle the situation gracefully.\n"
        f"Context fields: {', '.join(context_fields)}\n"
        f"Current context: {json.dumps(context)}\n"
        f"Current workflow step: {context.get('substep', 'greet')}\n"
        f"Workflow steps (in order):\n" + "\n".join([
            f"- {step['substep']}: {step['description']} (extract: {', '.join(step['extract']) if step['extract'] else 'none'})" for step in workflow
        ]) + "\n"
        f"Example:\nCaregiver: I need help with my schedule.\nAgent: Sure, what do you need help with regarding your schedule?\n" \
        f"After your response, append a delimiter '---EXTRACTED---' and then the extracted data as JSON on a new line. Do not write anything like ``` json ``` or anything like that.\n"
        f"The extracted JSON should include any relevant fields and MUST include the next substep as 'substep'.\n"
    )
    conversation = [SystemMessage(content=system_prompt)]
    if user_input:
        conversation.append(HumanMessage(content=user_input))
    else:
        conversation.append(HumanMessage(content=""))
    response = llm.invoke(conversation)
    content = response.content
    if '---EXTRACTED---' in content:
        reply, extracted = content.split('---EXTRACTED---', 1)
        reply = reply.strip()
        if not reply.endswith('\n'):
            reply = reply + '\n'
        extracted = extracted.strip()
        try:
            extracted_json = json.loads(extracted)
        except Exception:
            extracted_json = {}
    else:
        reply = content.strip()
        extracted_json = {}
    if isinstance(extracted_json, dict):
        context.update({k: v for k, v in extracted_json.items() if v is not None})
    if extracted_json.get("substep"):
        context["substep"] = extracted_json["substep"]
    return {"messages": messages + [SystemMessage(content=reply)], "context_data": context}