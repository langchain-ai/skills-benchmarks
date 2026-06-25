Use snake_case tool names:

```python
# BAD: Invalid tool name
@tool(name="Get Weather!")  # Special chars not allowed
def bad_tool() -> str:
    return "result"

# GOOD: Use snake_case
@tool(name="get_weather")  # Valid name
def good_tool() -> str:
    return "result"
```
