Handle validation errors with try/except.

```python
from langchain.agents import create_agent
from pydantic import BaseModel, Field, ValidationError

class StrictSchema(BaseModel):
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: int = Field(ge=0, le=120)

agent = create_agent(
    model="gpt-4.1",
    response_format=StrictSchema,
)

try:
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Email: invalid, Age: -5"}]
    })
except ValidationError as e:
    print(f"Validation failed: {e}")
```
