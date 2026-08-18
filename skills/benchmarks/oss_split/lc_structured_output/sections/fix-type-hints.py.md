Always use type hints for fields.

```python
# Problem: Missing type hints
class Data(BaseModel):
    items = []  # No type hint!

# Solution: Always use type hints
from typing import List

class Data(BaseModel):
    items: List[str] = Field(default_factory=list)
```
