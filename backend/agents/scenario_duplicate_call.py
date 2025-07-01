from langchain_core.messages import SystemMessage

def duplicate_call_node(state):
    prompt = "No call is needed for duplicate clock-in/out. The call will be rejected."
    return {"messages": state["messages"] + [SystemMessage(content=prompt)]} 