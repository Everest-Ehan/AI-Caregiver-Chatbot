from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

def wrong_phone_node(state):
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
        "phone_response",
        "app_works",
        "coordinator_ok",
        "substep"
    ]
    workflow = [
        {"substep": "greet", "description": "Greet and explain wrong phone usage.", "extract": []},
        {"substep": "get_phone_response", "description": "Ask if they can use the client's house phone.", "extract": ["phone_response"]},
        {"substep": "app_option", "description": "If client won't allow, ask if HHA app works.", "extract": ["app_works"]},
        {"substep": "coordinator_setup", "description": "If app doesn't work, offer coordinator call.", "extract": ["coordinator_ok"]},
        {"substep": "end", "description": "End the conversation politely.", "extract": []},
    ]
    scenario_examples = """
Example 1:
Caregiver: Sorry, I'll use the client's phone next time.
Agent: No problem! Please feel free to call us if you have any other issues.

Example 2:
Caregiver: Client won't allow me to use their phone.
Agent: In this situation I would recommend you use the HHA app to clock in. Does your app work?
Caregiver: My app doesn't work.
Agent: I can have one of our care coordinators give you a call and get your HHA app set up. Does that sound good to you?
Caregiver: Yes, that would be helpful!
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
        f"Example:\nCaregiver: Client won't allow me to use their phone.\nAgent: In this situation I would recommend you use the HHA app to clock in. Does your app work?\n" \
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