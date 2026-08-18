Add custom tools to agent:

```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It is always sunny in {city}"

agent = create_deep_agent(
    tools=[get_weather],
    system_prompt="You are a helpful weather assistant"
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What's the weather in Tokyo?"}
    ]
})
```
