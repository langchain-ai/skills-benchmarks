Bind a tool to a model and inspect the tool_calls returned by the model.
```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}: Sunny, 72F"

model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke("What's the weather in SF?")
print(response.tool_calls)
# [{'name': 'get_weather', 'args': {'location': 'San Francisco'}, 'id': 'call_abc123'}]
```
