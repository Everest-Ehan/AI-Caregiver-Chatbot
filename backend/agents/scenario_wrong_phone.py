from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def wrong_phone_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    context = state.get("context_data", {})
    if not context.get("client_phone"):
        prompt = "Please use the client's house phone to clock in. Can you provide the client's phone number?"
        return {"messages": state["messages"] + [SystemMessage(content=prompt)]}
    # Continue branching as needed for other sub-steps
    prompt = f"Thank you. Please use the correct phone for future clock-ins."
    return {"messages": state["messages"] + [SystemMessage(content=prompt)]} 