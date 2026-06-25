Define a complex schema with nested objects and validated fields.
```python
from pydantic import BaseModel, Field
from typing import List, Optional

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
```
