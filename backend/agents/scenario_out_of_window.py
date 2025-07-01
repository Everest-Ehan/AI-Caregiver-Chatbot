from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def out_of_window_node(state):
    print("out of window node")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    # Step 1: Greet and confirm reason for lateness
    if substep == "greet":
        prompt = "Hello, this is Rosella from Independence Care. How are you doing today? I have noticed that you clocked in late for your shift today, I just wanted to confirm what was the reason for that?"
        context["substep"] = "get_late_reason"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: Get reason for being late
    if substep == "get_late_reason":
        if not context.get("late_reason") and user_input:
            extracted = extract_context_field(user_input, "late_reason", "Extract the reason for being late (forgot to clock in, woke up late, doctor appointment, client asked to come late, etc.)")
            if extracted.get("late_reason"):
                context["late_reason"] = extracted["late_reason"]
        if not context.get("late_reason"):
            prompt = "Can you tell me what was the reason for being late today?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        # Check if it's "forgot to clock in" scenario
        if "forgot" in str(context["late_reason"]).lower() or "didn't clock" in str(context["late_reason"]).lower():
            prompt = "Oh! I totally understand, can you tell me what time you actually arrived today?"
            context["substep"] = "get_actual_arrival_time"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            # Other reasons (woke up late, appointment, etc.)
            prompt = "Okay, can you tell me what time you actually arrived today?"
            context["substep"] = "get_actual_arrival_time"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 3: Get actual arrival time
    if substep == "get_actual_arrival_time":
        if not context.get("actual_arrival_time") and user_input:
            extracted = extract_context_field(user_input, "actual_arrival_time", "Extract the actual arrival time (e.g., 9am, 9:05, etc.)")
            if extracted.get("actual_arrival_time"):
                context["actual_arrival_time"] = extracted["actual_arrival_time"]
        if not context.get("actual_arrival_time"):
            prompt = "What time did you actually arrive today?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "That's great, can you also put the client on the phone so we can confirm with them?"
        context["substep"] = "get_client_on_phone"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 4: Get client on phone
    if substep == "get_client_on_phone":
        if not context.get("client_on_phone") and user_input:
            extracted = extract_context_field(user_input, "client_on_phone", "Return yes if the client is on the phone or available")
            if extracted.get("client_on_phone"):
                context["client_on_phone"] = extracted["client_on_phone"]
        if not context.get("client_on_phone"):
            prompt = "Can you put the client on the phone so I can confirm the arrival time?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "Hi, can you state your name?"
        context["substep"] = "get_client_name"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 5: Get client name
    if substep == "get_client_name":
        if not context.get("client_name") and user_input:
            extracted = extract_context_field(user_input, "client_name", "Extract the client's name")
            if extracted.get("client_name"):
                context["client_name"] = extracted["client_name"]
        if not context.get("client_name"):
            prompt = "Can you please state your name?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = f"Great, can you confirm what time your aide showed up today?"
        context["substep"] = "confirm_arrival_time"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 6: Confirm arrival time with client
    if substep == "confirm_arrival_time":
        if not context.get("client_confirmed_time") and user_input:
            extracted = extract_context_field(user_input, "client_confirmed_time", "Extract the time the client confirms the aide arrived")
            if extracted.get("client_confirmed_time"):
                context["client_confirmed_time"] = extracted["client_confirmed_time"]
        if not context.get("client_confirmed_time"):
            prompt = "What time did your aide arrive today?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        # Calculate adjusted end time (add the difference to end time)
        arrival_time = context.get("client_confirmed_time", "9:05")
        prompt = f"Great, thank you. We will adjust the schedule for a start time of {arrival_time}. We will adjust the scheduled clock out time accordingly, so you do not lose any hours today. Can you put your aide back on the phone please?"
        context["substep"] = "back_to_caregiver"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 7: Back to caregiver
    if substep == "back_to_caregiver":
        if not context.get("caregiver_back") and user_input:
            extracted = extract_context_field(user_input, "caregiver_back", "Return yes if the caregiver is back on the phone")
            if extracted.get("caregiver_back"):
                context["caregiver_back"] = extracted["caregiver_back"]
        if not context.get("caregiver_back"):
            prompt = "Can you put your aide back on the phone?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        arrival_time = context.get("client_confirmed_time", "9:05")
        office_location = context.get("office_location", "our office")
        prompt = f"Hi, so the client confirmed you showed up at {arrival_time} so your schedule has been adjusted to reflect that arrival time. Moving forward, I want to let you know that we are not allowed to make any changes to any clock in or clock out time. So, going forward please make sure you are very careful with your clock in and clock out because we will not be able to adjust them due to {office_location} state law. Thank you, have a good day!"
        context["substep"] = "end"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 8: End
    if substep == "end":
        prompt = "Thank you, you too."
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you. All information received."
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 