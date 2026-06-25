Ensure Pydantic v2 is installed.

```python
# Some LangChain versions require Pydantic v2
# May cause errors with Pydantic v1
from pydantic import BaseModel

class Output(BaseModel):
    name: str

# Ensure Pydantic v2 is installed
# pip install "pydantic>=2.0"
```
