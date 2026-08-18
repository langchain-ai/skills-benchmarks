Raising exceptions in tools:

```python
from langchain.tools import tool

@tool
def divide(numerator: float, denominator: float) -> float:
    """Divide two numbers.

    Args:
        numerator: The number to divide
        denominator: The number to divide by
    """
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator

# Error will be caught and returned as ToolMessage
```
