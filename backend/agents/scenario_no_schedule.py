from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def no_schedule_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
    # Step 1: Greet and confirm client
    if substep == "greet":
        prompt = "Hello, this is Rosella from Independence Care. How are you doing today? Can you confirm the client you are working with today?"
        context["substep"] = "get_client_name"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: Get client name
    if substep == "get_client_name":
        if not context.get("client_name") and user_input:
            extracted = extract_context_field(user_input, "client_name")
            if extracted.get("client_name"):
                context["client_name"] = extracted["client_name"]
        if not context.get("client_name"):
            prompt = "Can you please provide the client name?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = f"Thank you for confirming, {context['client_name']}. Is this your regular schedule?"
        context["substep"] = "get_regular_schedule"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 3: Get regular schedule
    if substep == "get_regular_schedule":
        if not context.get("regular_schedule") and user_input:
            extracted = extract_context_field(user_input, "regular_schedule","If the client says, please say also add no in the regular schedule field too. If he says only yes, return yes in field")
            if extracted.get("regular_schedule"):
                context["regular_schedule"] = extracted["regular_schedule"]
        if not context.get("regular_schedule"):
            prompt = "Is this your regular schedule? If not, what is your regular schedule?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        if str(context["regular_schedule"]).lower() in ["no", "not my regular schedule"]:
            prompt = "Which day would you like to remove from your schedule this week?"
            context["substep"] = "remove_day"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "Thank you for confirming your regular schedule. Can you bring the client to the phone so I can confirm the change?"
            context["substep"] = "confirm_with_client"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 4: Remove a day (if not regular schedule)
    if substep == "remove_day":
        if not context.get("remove_day") and user_input:
            extracted = extract_context_field(user_input, "remove_day")
            if extracted.get("remove_day"):
                context["remove_day"] = extracted["remove_day"]
        if not context.get("remove_day"):
            prompt = "Please specify which day to remove."
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "Can you bring the client to the phone so I can confirm the change?"
        context["substep"] = "confirm_with_client"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 5: Confirm with client
    if substep == "confirm_with_client":
        if not context.get("client_on_phone") and user_input:
            extracted = extract_context_field(user_input, "client_on_phone", "return yes in field if the client is on the phone")
            if extracted.get("client_on_phone"):
                context["client_on_phone"] = extracted["client_on_phone"]
        if not context.get("client_on_phone"):
            prompt = "Is the client on the phone? Please have them confirm their name."
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = f"Thank you, {context.get('client_name', 'client')}. Can you confirm that the caregiver can swap any other day of the week for today?"
        context["substep"] = "confirm_swap"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 6: Confirm swap
    if substep == "confirm_swap":
        if not context.get("swap_confirmed") and user_input:
            extracted = extract_context_field(user_input, "swap_confirmed", "return yes in field if the client confirms the swap")
            if extracted.get("swap_confirmed"):
                context["swap_confirmed"] = extracted["swap_confirmed"]
        if not context.get("swap_confirmed"):
            prompt = "Can you confirm the swap is okay?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "Great, your caregiver will be with you today and will no longer be scheduled for the removed day. Can I help you with anything else?"
        context["substep"] = "end"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 7: End
    if substep == "end":
        prompt = "Okay, have a great day!"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you. All information received."
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 