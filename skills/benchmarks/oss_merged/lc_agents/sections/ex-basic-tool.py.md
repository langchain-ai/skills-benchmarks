Define a calculator tool using the @tool decorator with typed parameters.
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

    Args:
        operation: The mathematical operation to perform
        a: First number
        b: Second number
    """
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return ops[operation]
```
