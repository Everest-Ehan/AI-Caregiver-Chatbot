from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def gps_out_of_range_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    if not context.get("clock_in_location"):
        prompt = "Can you confirm your current location for clock-in?"
        return {"messages": state["messages"] + [SystemMessage(content=prompt)]}
    # Continue branching as needed for other sub-steps
    prompt = f"Thank you. Please try to clock in again at the correct location."
    return {"messages": state["messages"] + [SystemMessage(content=prompt)]} 