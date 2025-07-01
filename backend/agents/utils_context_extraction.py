from langchain_openai.chat_models import ChatOpenAI
import json

def extract_context_field(user_input, field_name, optionalMessage=""):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = (
        f"Extract the '{field_name}' from this message: '{user_input}'. {optionalMessage}"
        f"If present, return as JSON: {{\"{field_name}\": value}}. Only JSON as. "
        f"If not present, return an empty JSON object."
    )
    response = llm.invoke(prompt)
    content = response.content.strip()
    # Strip first and last line to remove any extra text
    lines = content.split('\n')
    if len(lines) > 2:
        content = '\n'.join(lines[1:-1]).strip()
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {} 