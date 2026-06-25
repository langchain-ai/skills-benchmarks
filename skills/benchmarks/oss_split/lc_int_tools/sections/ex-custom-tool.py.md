Define custom tool with @tool decorator.

```python
from langchain_core.tools import tool
from typing import Optional

@tool
def get_weather(location: str, unit: Optional[str] = "celsius") -> str:
    """Get the current weather for a location.

    Args:
        location: The city name, e.g., 'San Francisco'
        unit: Temperature unit, either 'celsius' or 'fahrenheit'
    """
    # Your implementation
    data = fetch_weather(location, unit)
    return f"The weather in {location} is {data['temp']}°{unit[0].upper()}"

# Use with agent
from langchain.agents import create_agent

agent = create_agent(model="gpt-4.1", tools=[get_weather])

response = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in London?"}]
})
```
