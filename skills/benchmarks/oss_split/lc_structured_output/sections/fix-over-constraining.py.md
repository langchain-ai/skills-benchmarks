Avoid overly strict regex patterns.

```python
import re

# Problem: Too strict for model
class Data(BaseModel):
    code: str = Field(pattern=r"^[A-Z]{2}-\d{4}-[A-Z]{3}$")  # Very specific!

# Solution: Use looser validation or describe format
class Data(BaseModel):
    code: str = Field(description="Format: XX-0000-XXX (letters and numbers)")
```
