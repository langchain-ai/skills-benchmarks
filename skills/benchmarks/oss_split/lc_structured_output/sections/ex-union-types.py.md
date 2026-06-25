Union types for multiple possible schemas.

```python
from pydantic import BaseModel
from typing import Union, Literal

class EmailContact(BaseModel):
    type: Literal["email"]
    to: str
    subject: str

class PhoneContact(BaseModel):
    type: Literal["phone"]
    number: str
    message: str

ContactMethod = Union[EmailContact, PhoneContact]

agent = create_agent(
    model="gpt-4.1",
    response_format=ContactMethod,
)
# Model chooses which schema based on input
```
