Optional fields and default values.

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class Event(BaseModel):
    title: str
    date: str
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    confirmed: bool = False
```
