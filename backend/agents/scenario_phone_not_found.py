from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def phone_not_found_node(state):
    print("phone not found node")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    
    print(substep)
    # Step 1: Greet and identify unregistered phone
    if substep == "greet":
        phone_number = context.get("unregistered_phone", "this number")
        prompt = f"Hello, this is Rosella from Independence Care. How are you doing today? I have noticed that you have clocked in using a phone number that is not registered with us. Can you confirm whose number this is? ({phone_number})"
        context["substep"] = "confirm_phone_owner"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: Confirm phone owner
    if substep == "confirm_phone_owner":
        if not context.get("phone_owner") and user_input:
            extracted = extract_context_field(user_input, "phone_owner", "Extract who owns the phone (client, caregiver, etc.)")
            if extracted.get("phone_owner"):
                context["phone_owner"] = extracted["phone_owner"]
        if not context.get("phone_owner"):
            prompt = "Can you confirm whose phone number this is?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        # Check if it's client's new phone
        if "client" in str(context["phone_owner"]).lower():
            prompt = "Okay, can your client confirm that?"
            context["substep"] = "client_confirmation"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "Can you please use a registered phone number for clocking in?"
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 3: Get client confirmation
    if substep == "client_confirmation":
        if not context.get("client_can_confirm") and user_input:
            extracted = extract_context_field(user_input, "client_can_confirm", "Return yes if client can confirm, no if they cannot")
            if extracted.get("client_can_confirm"):
                context["client_can_confirm"] = extracted["client_can_confirm"]
        if not context.get("client_can_confirm"):
            prompt = "Can your client confirm this is their new phone number?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["client_can_confirm"]).lower() in ["yes", "they can", "sure"]:
            prompt = "Perfect! Can you get your client on the phone?"
            context["substep"] = "get_client_on_phone"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "I understand. Please use a registered phone number for future clock-ins."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 4: Get client on phone
    if substep == "get_client_on_phone":
        if not context.get("client_on_phone") and user_input:
            extracted = extract_context_field(user_input, "client_on_phone", "Return yes if client is on the phone")
            if extracted.get("client_on_phone"):
                context["client_on_phone"] = extracted["client_on_phone"]
        if not context.get("client_on_phone"):
            prompt = "Can you put your client on the phone?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "Hello, this is Rosella from Independence Care, how are you doing today?"
        context["substep"] = "client_greeting"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 5: Client greeting response
    if substep == "client_greeting":
        if not context.get("client_doing") and user_input:
            extracted = extract_context_field(user_input, "client_doing", "Extract how client says they are doing")
            if extracted.get("client_doing"):
                context["client_doing"] = extracted["client_doing"]
        if not context.get("client_doing"):
            prompt = "How are you doing today?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "That's great to hear. Can you please confirm who I am talking to?"
        context["substep"] = "get_client_name"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 6: Get client name
    if substep == "get_client_name":
        if not context.get("client_name") and user_input:
            extracted = extract_context_field(user_input, "client_name", "Extract the client's name")
            if extracted.get("client_name"):
                context["client_name"] = extracted["client_name"]
        if not context.get("client_name"):
            prompt = "Can you please state your name?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        phone_number = context.get("unregistered_phone", "this number")
        prompt = f"Perfect! I just wanted to confirm if this is your new phone ({phone_number})"
        context["substep"] = "confirm_new_phone"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 7: Confirm new phone
    if substep == "confirm_new_phone":
        if not context.get("new_phone_confirmed") and user_input:
            extracted = extract_context_field(user_input, "new_phone_confirmed", "Return yes if client confirms it's their new phone")
            if extracted.get("new_phone_confirmed"):
                context["new_phone_confirmed"] = extracted["new_phone_confirmed"]
        if not context.get("new_phone_confirmed"):
            prompt = "Is this your new phone number?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["new_phone_confirmed"]).lower() in ["yes", "it is", "correct"]:
            prompt = "Great and will this be the number your caregiver will be using to clock in going forward?"
            context["substep"] = "future_use"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "I understand. Please use a registered phone number for clocking in."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 8: Confirm future use
    if substep == "future_use":
        if not context.get("future_use_confirmed") and user_input:
            extracted = extract_context_field(user_input, "future_use_confirmed", "Return yes if client confirms this will be used for future clock-ins")
            if extracted.get("future_use_confirmed"):
                context["future_use_confirmed"] = extracted["future_use_confirmed"]
        if not context.get("future_use_confirmed"):
            prompt = "Will this be the number used for future clock-ins?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["future_use_confirmed"]).lower() in ["yes", "think so", "probably"]:
            prompt = "Sounds great! Then I will make sure this gets updated in your profile. Thank you for your time. You guys have a good day."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "I understand. Please use a registered phone number for clocking in."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 9: End
    if substep == "end":
        prompt = "Thank you, have a good day!"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you. All information received."
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 