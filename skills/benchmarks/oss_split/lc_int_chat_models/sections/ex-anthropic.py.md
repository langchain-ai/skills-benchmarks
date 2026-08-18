Anthropic Claude with tool binding.

```python
from langchain_anthropic import ChatAnthropic
import os

model = ChatAnthropic(
    model="claude-3-opus-20240229",
    temperature=0.7,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=1024,
)

# Long context usage
response = model.invoke([
    {"role": "user", "content": "Analyze this long document..."}
])

# With tool use
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"The weather in {location} is sunny"

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("What's the weather in SF?")
```
