Return JSON-serializable data from tools:

```python
from datetime import datetime

# Problem: Returning non-serializable objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime objects need special handling

# Solution: Return serializable data
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()  # String is serializable
```
