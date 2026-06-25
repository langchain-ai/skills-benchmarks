Pydantic v2 vs v1 syntax differences.

```python
# Pydantic v2 (current)
from pydantic import BaseModel, Field

class Data(BaseModel):
    value: int = Field(ge=0, le=100)

# Pydantic v1 (legacy)
from pydantic import BaseModel, Field

class Data(BaseModel):
    value: int = Field(..., ge=0, le=100)  # Note the ...

    class Config:
        # v1 config
        pass
```
