Define tool and bind to model.

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# Define a tool
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72F"

# Bind tool to model
model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([get_weather])

# Model will decide to call the tool
response = model_with_tools.invoke("What's the weather in San Francisco?")

# Check if model called a tool
print(response.tool_calls)
# [{
#   'name': 'get_weather',
#   'args': {'location': 'San Francisco'},
#   'id': 'call_abc123'
# }]
```
