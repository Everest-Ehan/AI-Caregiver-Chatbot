from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

def no_schedule_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    # Define the scenario's context fields and workflow steps
    context_fields = [
        "client_name",
        "caregiver_name",
        "system_regular_schedule",
        "regular_schedule",
        "is_regular_schedule",
        "today_date",
        "today_shift",
        "remove_day",
        "client_on_phone",
        "client_name_confirmed",
        "swap_confirmed",
        "substep"
    ]
    workflow = [
        {"substep": "greet", "description": "Greet the caregiver and ask them to confirm the client they are working with today.", "extract": []},
        {"substep": "get_client_name", "description": "Thank the caregiver and ask if this is their regular schedule.", "extract": ["client_name"]},
        {"substep": "get_regular_schedule", "description": "If the regular schedule is not confirmed, ask what their regular schedule is. If it is not their regular schedule, ask which day to remove from their schedule this week.", "extract": ["regular_schedule", "is_regular_schedule"]},
        {"substep": "remove_day", "description": "Ask the caregiver to specify which day to remove.", "extract": ["remove_day"]},
        {"substep": "confirm_with_client", "description": "Ask the caregiver to bring the client to the phone to confirm the change only if the schedule is being changed (not regular schedule). Also confirm client name by asking client his name before asking to confirm change", "extract": ["client_on_phone", "client_name_confirmed"]},
        {"substep": "confirm_swap", "description": "Ask the client to confirm the swap is okay.", "extract": ["swap_confirmed"]},
        {"substep": "end", "description": "If it is the regular schedule, explain the app error and reassure the caregiver you will add them to the schedule and clock them in. If it is not the regular schedule, end the conversation politely after confirming with the client.", "extract": []}
    ]
    workflow_str = "Workflow steps (in order):\n" + "\n".join([
        f"- {step['substep']}: {step['description']} (extract: {', '.join(step['extract']) if step['extract'] else 'none'})" for step in workflow
    ])

    scenario_examples = """
Example 1 (No schedule, regular):
Caregiver: I work for John every Monday through Friday 9am to 5pm. Should I leave?
Agent: No, please do not leave. Unfortunately, the app can malfunction at times and remove Caregivers from schedules. I will add you to the schedule and clock you in. If for any reason this causes an error your coordinator will reach out to you to clarify.

Example 2 (No schedule, not regular, swap needed):
Caregiver: No, this is not my regular schedule. I usually do Mondays, Wednesdays and Fridays but the client asked me to come in today (Tuesday).
Agent: Okay, thank you for letting me know. You will have to remove one of your visits from the schedule this week, would you like to remove Wednesday or Friday?
Caregiver: Friday.
Agent: Okay, no problem. Can you just bring the client to the phone, so I can confirm the change with him?
...etc.
"""

    # Always send the full context fields and workflow to the LLM
    system_prompt = (
        f"You are Rosella from Independence Care, a professional caregiver support representative.\n"
        f"Your main job is to extract and update all relevant context fields for this scenario after each message.\n"
        f"Extraction rules (ALWAYS follow):\n"
        f"- After every message, extract and update ALL context fields you can infer from the conversation so far, even if not explicitly stated.\n"
        f"- You must always make sense of the conversation as a whole. If the user says something that logically means a context field should be set (e.g., if the client responds directly, set 'client_on_phone': true), update the extracted JSON accordingly, even if the user does not state it in the exact words.\n"
        f"- If a field is already present and valid, do not ask for it again.\n"
        f"- If a step logically requires a field to be true (e.g., if you are speaking to the client, set 'client_on_phone': true), set it in the extracted JSON.\n"
        f"- Only ask for missing or unclear information.\n"
        f"- If the caregiver is asked to remove a day from their schedule, only allow removal of days that are actually in their regular schedule. If the user tries to remove a day that is not in their regular schedule, politely inform them and ask them to choose a valid day.\n"
        f"- If the workflow is complete, set 'substep' to 'end'.\n"
        f"- If you need more information, keep the substep the same and ask for clarification.\n"
        f"- Never break, always handle the situation gracefully.\n"
        f"Context fields: {', '.join(context_fields)}\n"
        f"Current context: {json.dumps(context)}\n"
        f"Current workflow step: {context.get('substep', 'greet')}\n"
        f"Workflow steps (in order):\n" + "\n".join([
            f"- {step['substep']}: {step['description']} (extract: {', '.join(step['extract']) if step['extract'] else 'none'})" for step in workflow
        ]) + "\n"
        f"Example:\nCaregiver: Remove Thursday\nAgent: Thursday is not in your regular schedule. Please choose a day from your regular schedule to remove (e.g., Monday, Wednesday, or Friday).\n" 
        f"Example:\nCaregiver: Could you please bring Waleed to the phone?\nClient: Yes, I am here.\n(Extracted: 'client_on_phone': true)\n" 
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
    print(content)

    if '---EXTRACTED---' in content:
        reply, extracted = content.split('---EXTRACTED---', 1)
        reply = reply.strip()
        # Ensure reply ends with a single newline before the delimiter
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

    # Update context with all extracted fields, including substep
    if isinstance(extracted_json, dict):
        context.update({k: v for k, v in extracted_json.items() if v is not None})
    if extracted_json.get("substep"):
        context["substep"] = extracted_json["substep"]

    return {"messages": messages + [SystemMessage(content=reply)], "context_data": context}