Define and bind tools using decorators.

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Define a tool using decorator
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city name
    """
    return f"The weather in {location} is sunny and 72°F"

# Or define with Pydantic
class WeatherInput(BaseModel):
    location: str = Field(description="The city name")

@tool("get_weather", args_schema=WeatherInput)
def get_weather_pydantic(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny and 72°F"

# Bind tools to model
model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke("What's the weather in San Francisco?")
print(response.tool_calls)  # Model will suggest calling the weather tool
```
