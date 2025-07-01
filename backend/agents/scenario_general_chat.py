from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def general_chat_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    last_message = state["messages"][-1] if state["messages"] else None
    prompt = "You are a helpful and friendly AI assistant. Be conversational and helpful."
    conversation = [SystemMessage(content=prompt)]
    if last_message:
        conversation.append(HumanMessage(content=last_message.content if hasattr(last_message, 'content') else str(last_message)))
    response = llm.invoke(conversation)
    return {"messages": state["messages"] + [response]} 