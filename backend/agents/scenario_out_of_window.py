from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

def out_of_window_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    # Define context fields for this scenario
    context_fields = [
        "client_name",
        "caregiver_name",
        "scheduled_start_time",
        "actual_start_time",
        "late_reason",
        "client_on_phone",
        "client_name_confirmed",
        "client_confirmed_time",
        "can_makeup_hours",
        "makeup_time",
        "makeup_later",
        "substep"
    ]
    workflow = [
        {"substep": "greet", "description": "Greet and explain late clock-in detected.", "extract": []},
        {"substep": "get_late_reason", "description": "Ask for the reason for being late.", "extract": ["late_reason"]},
        {"substep": "get_actual_arrival_time", "description": "Ask for the actual arrival time.", "extract": ["actual_start_time"]},
        {"substep": "get_client_on_phone", "description": "Ask to bring the client to the phone.", "extract": ["client_on_phone"]},
        {"substep": "confirm_with_client", "description": "Ask the client to confirm the caregiver's arrival time and name.", "extract": ["client_name_confirmed", "client_confirmed_time"]},
        {"substep": "offer_makeup_hours", "description": "Offer to make up missed hours if late.", "extract": ["can_makeup_hours", "makeup_time", "makeup_later"]},
        {"substep": "end", "description": "End the conversation politely.", "extract": []}
    ]
    workflow_str = "Workflow steps (in order):\n" + "\n".join([
        f"- {step['substep']}: {step['description']} (extract: {', '.join(step['extract']) if step['extract'] else 'none'})" for step in workflow
    ])

    system_prompt = (
        f"You are Rosella from Independence Care, a professional caregiver support representative.\n"
        f"Your main job is to extract and update all relevant context fields for this scenario after each message.\n"
        f"Extraction rules (ALWAYS follow):\n"
        f"- After every message, extract and update ALL context fields you can infer from the conversation so far, even if not explicitly stated.\n"
        f"- You must always make sense of the conversation as a whole. If the user says something that logically means a context field should be set (e.g., if the client responds directly, set 'client_on_phone': true), update the extracted JSON accordingly, even if the user does not state it in the exact words.\n"
        f"- If a field is already present and valid, do not ask for it again.\n"
        f"- If a step logically requires a field to be true (e.g., if you are speaking to the client, set 'client_on_phone': true), set it in the extracted JSON.\n"
        f"- Only ask for missing or unclear information.\n"
        f"- If the caregiver cannot make up hours now but can later, set 'makeup_later' to true and end politely.\n"
        f"- If the workflow is complete, set 'substep' to 'end'.\n"
        f"- If you need more information, keep the substep the same and ask for clarification.\n"
        f"- Never break, always handle the situation gracefully.\n"
        f"Context fields: {', '.join(context_fields)}\n"
        f"Current context: {json.dumps(context)}\n"
        f"Current workflow step: {context.get('substep', 'greet')}\n"
        f"{workflow_str}\n"
        f"Example:\nCaregiver: No, I can’t right now but I can anytime later this week, I will call and let you guys know.\nAgent: Totally understand! If you decide you make up your hours, please feel free to let us know.\n(Extracted: 'makeup_later': true)\n"
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