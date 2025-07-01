from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def duplicate_call_node(state):
    print("duplicate call node")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    # Step 1: Greet and explain duplicate call
    if substep == "greet":
        prompt = "Hello, this is Rosella from Independence Care. How are you doing today? I have noticed that you have made a duplicate clock-in/out call. No call is needed for duplicate clock-in/out. The call will be rejected."
        context["substep"] = "end"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: End
    if substep == "end":
        prompt = "Thank you, have a good day!"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you. All information received."
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 