Model calls multiple tools in parallel.

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather."""
    return f"Weather in {location}: Sunny"

@tool
def get_news(topic: str) -> str:
    """Get news."""
    return f"Latest news about {topic}"

model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([get_weather, get_news])

response = model_with_tools.invoke("Get weather for NYC and news about AI")

# Model may call both tools in parallel
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'NYC'}, 'id': 'call_1'},
#   {'name': 'get_news', 'args': {'topic': 'AI'}, 'id': 'call_2'}
# ]
```
