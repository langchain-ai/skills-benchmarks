Define nested Pydantic models for complex data.

```python
from pydantic import BaseModel, Field
from typing import List

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str

class Person(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: str
    address: Address
    tags: List[str] = Field(default_factory=list)

agent = create_agent(
    model="gpt-4.1",
    response_format=Person,
)
```
