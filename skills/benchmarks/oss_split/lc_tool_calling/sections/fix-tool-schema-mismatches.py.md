Match parameter names exactly in schema.

```python
# Problem: Args don't match function signature
@tool
def get_weather(location: str, units: str = "celsius") -> str:
    """Get weather."""
    return f"Weather in {location}"

# Model calls: {"location": "NYC", "unit": "fahrenheit"}  # Wrong key!

# Solution: Match parameter names exactly
# Model will call: {"location": "NYC", "units": "fahrenheit"}
# Or use Field() for better descriptions
from pydantic import Field

@tool
def get_weather(
    location: str = Field(description="City name"),
    units: str = Field(default="celsius", description="celsius or fahrenheit")
) -> str:
    """Get weather for a location."""
    return f"Weather in {location} ({units})"
```
