from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def phone_not_found_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    if not context.get("new_phone_number"):
        prompt = "Can you provide the new phone number used to clock in?"
        return {"messages": state["messages"] + [SystemMessage(content=prompt)]}
    # Continue branching as needed for other sub-steps
    prompt = f"Thank you. We'll update your profile with the new phone number."
    return {"messages": state["messages"] + [SystemMessage(content=prompt)]} 