from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .utils_context_extraction import extract_context_field

def general_chat_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    substep = context.get("substep", "greet")
    messages = state["messages"]
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break

    # Step 1: Greet and start general conversation
    if substep == "greet":
        prompt = "Hello, this is Rosella from Independence Care. How are you doing today? How can I help you today?"
        context["substep"] = "conversation"
        return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Step 2: General conversation
    if substep == "conversation":
        if user_input:
            # Use LLM to generate a conversational response
            conversation = [
                SystemMessage(content="You are Rosella from Independence Care, a professional caregiver support representative. Be helpful, friendly, and professional. Keep responses concise and relevant to caregiver support."),
                HumanMessage(content=user_input)
            ]
            response = llm.invoke(conversation)
            return {"messages": messages + [response], "context_data": context}
        else:
            prompt = "How can I help you today?"
            return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context}

    # Fallback
    prompt = "Thank you for contacting Independence Care. How can I assist you?"
    return {"messages": messages + [SystemMessage(content=prompt)], "context_data": context} 