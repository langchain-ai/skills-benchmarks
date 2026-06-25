Calculator with @tool decorator:

```python
from langchain.tools import tool
from typing import Literal

@tool
def calculator(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> float:
    """Perform mathematical calculations.

    Use this when you need to compute numbers.

    Args:
        operation: The mathematical operation to perform
        a: First number
        b: Second number
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

result = calculator.invoke({"operation": "add", "a": 5, "b": 3})
print(result)  # "8.0"
```
