from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def gps_out_of_range_node(state):
    print("gps out of range node")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    # Step 1: Greet and identify GPS issue
    if substep == "greet":
        prompt = "Hello, this is Rosella from Independence Care. How are you doing today? I have noticed you have clocked in outside of the client's service area, which is not close to your client's house. Can you please clock in again once you are at your client's house, because we are not able to accept this clock in."
        context["substep"] = "get_clock_in_location"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: Get clock-in location response
    if substep == "get_clock_in_location":
        if not context.get("clock_in_location") and user_input:
            extracted = extract_context_field(user_input, "clock_in_location", "Extract where the caregiver says they clocked in (client's house, different location, etc.)")
            if extracted.get("clock_in_location"):
                context["clock_in_location"] = extracted["clock_in_location"]
        if not context.get("clock_in_location"):
            prompt = "Where did you clock in from?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        # Check if they claim it's the client's house
        if "client" in str(context["clock_in_location"]).lower() or "house" in str(context["clock_in_location"]).lower():
            prompt = "I am sorry to hear that but it can't be the application's fault because all of our caregivers are using the same application and this does not seem to be the issue with anyone else at the moment, but can you try to clock in again and make sure you are inside your client's house."
            context["substep"] = "try_again"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            # They admit it's not at client's house
            prompt = "Can you please clock in again once you are at your client's house?"
            context["substep"] = "try_again"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 3: Try again response
    if substep == "try_again":
        if not context.get("can_try_again") and user_input:
            extracted = extract_context_field(user_input, "can_try_again", "Return yes if they can try again, no if they cannot")
            if extracted.get("can_try_again"):
                context["can_try_again"] = extracted["can_try_again"]
        if not context.get("can_try_again"):
            prompt = "Can you try clocking in again from your client's house?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        
        if str(context["can_try_again"]).lower() in ["no", "can't", "won't"]:
            prompt = "Oh! Okay there should be an option in your app called 'unscheduled visits' try doing it from there and see if it lets you!"
            context["substep"] = "unscheduled_visit"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        else:
            prompt = "Thank you, please feel free to reach us if you come across any problems. Remember it is our state law that a Home Care agency cannot bill for visits that are rendered outside of the client's home."
            context["substep"] = "end"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 4: Unscheduled visit response
    if substep == "unscheduled_visit":
        if not context.get("unscheduled_visit_response") and user_input:
            extracted = extract_context_field(user_input, "unscheduled_visit_response", "Extract their response about trying unscheduled visit")
            if extracted.get("unscheduled_visit_response"):
                context["unscheduled_visit_response"] = extracted["unscheduled_visit_response"]
        if not context.get("unscheduled_visit_response"):
            prompt = "Can you try the unscheduled visit option?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}
        prompt = "Thank you, please feel free to reach us if you come across any problems. Remember it is our state law that a Home Care agency cannot bill for visits that are rendered outside of the client's home."
        context["substep"] = "end"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 5: End
    if substep == "end":
        prompt = "Thank you, have a good day!"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you. All information received."
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 