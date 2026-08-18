Use Pydantic model for tool input validation.

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="The city name")
    unit: str = Field(default="celsius", description="Temperature unit")

@tool("get_weather", args_schema=WeatherInput)
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather for a location."""
    # Implementation
    return f"Weather in {location}: 72°{unit[0].upper()}"

# Tool now has proper schema validation
```
