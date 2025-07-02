from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

def gps_out_of_range_node(state):
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
        "gps_issue_type",  # 'clock_in' or 'clock_out'
        "clock_in_location",
        "clock_out_location",
        "can_try_again",
        "unscheduled_visit_attempted",
        "errand_reason",  # generalized reason for being out of range
        "client_on_phone",
        "client_confirmed_reason",
        "office_state",
        "substep"
    ]
    workflow = [
        {"substep": "greet", "description": "Greet and explain GPS issue (clock-in or clock-out).", "extract": ["gps_issue_type"]},
        {"substep": "get_location", "description": "Ask where they clocked in/out.", "extract": ["clock_in_location", "clock_out_location"]},
        {"substep": "get_reason", "description": "Ask for the reason for being out of range (errand, mistake, etc).", "extract": ["errand_reason"]},
        {"substep": "try_again", "description": "Ask if they can try again at the correct location.", "extract": ["can_try_again"]},
        {"substep": "unscheduled_visit", "description": "If can't try again, suggest unscheduled visit option.", "extract": ["unscheduled_visit_attempted"]},
        {"substep": "client_confirmation", "description": "Ask client to confirm the reason if needed.", "extract": ["client_on_phone", "client_confirmed_reason"]},
        {"substep": "end", "description": "End the conversation politely, remind about state law.", "extract": []},
    ]
    scenario_examples = """
Example 1 (Clock-in):
Caregiver: I clocked in from my car.
Agent: Please clock in again once you are at your client's house, because we are not able to accept this clock in.

Example 2 (Errand):
Caregiver: I stopped by to pick up groceries and medicine for the client before coming in.
Agent: Can your client confirm that you picked up these items for them before your shift?
Caregiver: Yes, you can ask them.
Agent: (calls client to confirm)

Example 3 (Clock-out):
Agent: I have noticed your clock out is outside of the client's service area, and we are not able to accept that. Can you please go back and clock out from your client’s house? Because we can’t complete the visit without your clock out.
Caregiver: I have already left my client's house, and I am not able to go back!
Agent: I apologize for the inconvenience this causes but we will not be able to mark your shift as completed without a clock out, so it is really important. Again, I apologize for the inconvenience this is causing.
"""
    system_prompt = (
        f"You are Rosella from Independence Care, a professional caregiver support representative.\n"
        f"Your main job is to extract and update all relevant context fields for this scenario after each message.\n"
        f"Extraction rules (ALWAYS follow):\n"
        f"- After every message, extract and update ALL context fields you can infer from the conversation so far, even if not explicitly stated.\n"
        f"- Always make sense of the conversation as a whole. If the user says something that logically means a context field should be set (e.g., if the client responds directly, set 'client_on_phone': true), update the extracted JSON accordingly.\n"
        f"- If a field is already present and valid, do not ask for it again.\n"
        f"- Only ask for missing or unclear information.\n"
        f"- If the caregiver was out of range for a valid reason (errand, etc.), ask the client to confirm.\n"
        f"- If the workflow is complete, set 'substep' to 'end'.\n"
        f"- If you need more information, keep the substep the same and ask for clarification.\n"
        f"- Never break, always handle the situation gracefully.\n"
        f"Context fields: {', '.join(context_fields)}\n"
        f"Current context: {json.dumps(context)}\n"
        f"Current workflow step: {context.get('substep', 'greet')}\n"
        f"Workflow steps (in order):\n" + "\n".join([
            f"- {step['substep']}: {step['description']} (extract: {', '.join(step['extract']) if step['extract'] else 'none'})" for step in workflow
        ]) + "\n"
        f"Example:\nCaregiver: I clocked out from the store.\nAgent: What was the reason for clocking out there?\n" \
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