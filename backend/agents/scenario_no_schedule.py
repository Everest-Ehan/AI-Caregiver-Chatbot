from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def no_schedule_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    # Example: ask for client name if not present
    context = state.get("context_data", {})
    if not context.get("client_name"):
        prompt = "Please provide the client name."
        return {"messages": state["messages"] + [SystemMessage(content=prompt)]}
    # Continue branching as needed for other sub-steps
    # ...
    # If all info present, resolve
    prompt = f"Thank you. All information received: {context}"
    return {"messages": state["messages"] + [SystemMessage(content=prompt)]} 