Define a calculator tool using the @tool decorator with parameter types.
```python
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: Math expression like "2 + 2" or "10 * 5"
    """
    allowed = set('0123456789+-*/(). ')
    if not all(c in allowed for c in expression):
        return "Error: Invalid characters in expression"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"
```
