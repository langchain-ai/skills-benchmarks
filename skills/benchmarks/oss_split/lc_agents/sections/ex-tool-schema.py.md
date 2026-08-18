Tool with typed parameters:

```python
from langchain.tools import tool
from typing import Literal

@tool
def calculate(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> float:
    """Perform a mathematical calculation.

    Args:
        operation: The operation to perform
        a: First number
        b: Second number
    """
    ops = {"add": lambda: a + b, "subtract": lambda: a - b, "multiply": lambda: a * b, "divide": lambda: a / b}
    return ops[operation]()
```
