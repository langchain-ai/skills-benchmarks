Using StructuredTool for full control:

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    operation: str = Field(description="Operation to perform")
    a: float = Field(description="First number")
    b: float = Field(description="Second number")

def _calculate(operation: str, a: float, b: float) -> float:
    """Internal calculation logic."""
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y,
    }
    return operations[operation](a, b)

calculator_tool = StructuredTool.from_function(
    func=_calculate,
    name="calculator",
    description="Perform mathematical calculations",
    args_schema=CalculatorInput,
)
```
