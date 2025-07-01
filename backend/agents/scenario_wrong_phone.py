from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def wrong_phone_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
        
    # Step 1: Greet and identify wrong phone usage
    if substep == "greet":
        prompt = "Hello, this is Rosella from Independence Care. How are you doing today? I have noticed that you used the IVR number to clock in today, but you used your phone to call that number instead of the client's house phone. Can you please clock in again using the client's house phone?"
        context["substep"] = "get_phone_response"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: Get response about using client's phone
    if substep == "get_phone_response":
        if not context.get("phone_response") and user_input:
            extracted = extract_context_field(user_input, "phone_response", "Extract their response about using client's phone (will do it, client won't allow, etc.)")
            if extracted.get("phone_response"):
                context["phone_response"] = extracted["phone_response"]
        if not context.get("phone_response"):
            prompt = "Can you please use the client's house phone to clock in?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        # Check if they can use client's phone
        if "sorry" in str(context["phone_response"]).lower() or "will do" in str(context["phone_response"]).lower():
            prompt = "No problem! Please feel free to call us if you have any other issues."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        elif "won't allow" in str(context["phone_response"]).lower() or "client won't" in str(context["phone_response"]).lower():
            prompt = "That's unfortunate, in this situation I would recommend you use the HHA app to clock in."
            context["substep"] = "app_option"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "Can you please use the client's house phone to clock in?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 3: App option response
    if substep == "app_option":
        if not context.get("app_works") and user_input:
            extracted = extract_context_field(user_input, "app_works", "Return yes if app works, no if it doesn't work")
            if extracted.get("app_works"):
                context["app_works"] = extracted["app_works"]
        if not context.get("app_works"):
            prompt = "Does your HHA app work for clocking in?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["app_works"]).lower() in ["no", "doesn't work", "not working"]:
            prompt = "Okay, for that I can have one of our care coordinators give you a call and get your HHA app set up. Does that sound good to you?"
            context["substep"] = "coordinator_setup"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "Great! Please use the HHA app to clock in from now on."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 4: Coordinator setup response
    if substep == "coordinator_setup":
        if not context.get("coordinator_ok") and user_input:
            extracted = extract_context_field(user_input, "coordinator_ok", "Return yes if they want coordinator help, no if they don't")
            if extracted.get("coordinator_ok"):
                context["coordinator_ok"] = extracted["coordinator_ok"]
        if not context.get("coordinator_ok"):
            prompt = "Would you like a care coordinator to help set up your HHA app?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["coordinator_ok"]).lower() in ["yes", "sounds good", "helpful"]:
            prompt = "Great! I will relay this message to them, and someone will contact you shortly, is there anything else I can assist you with today?"
            context["substep"] = "anything_else"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "I understand. Please try to use the client's house phone for future clock-ins."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 5: Anything else
    if substep == "anything_else":
        if not context.get("anything_else") and user_input:
            extracted = extract_context_field(user_input, "anything_else", "Return yes if they need more help, no if they don't")
            if extracted.get("anything_else"):
                context["anything_else"] = extracted["anything_else"]
        if not context.get("anything_else"):
            prompt = "Is there anything else I can help you with?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["anything_else"]).lower() in ["no", "that's all", "nothing else"]:
            prompt = "Okay, then you have a good day ahead. Take care, bye!"
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "What else can I help you with?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 6: End
    if substep == "end":
        prompt = "Thank you, have a good day!"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you. All information received."
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 