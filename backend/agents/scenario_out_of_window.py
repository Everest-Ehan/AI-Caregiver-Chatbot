from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def out_of_window_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    if not context.get("late_reason"):
        prompt = "Can you tell me the reason for being late?"
        return {"messages": state["messages"] + [SystemMessage(content=prompt)]}
    # Continue branching as needed for other sub-steps
    prompt = f"Thank you for explaining. We'll adjust your schedule as needed."
    return {"messages": state["messages"] + [SystemMessage(content=prompt)]} 