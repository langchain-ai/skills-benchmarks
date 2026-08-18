Return serializable types:

```python
from datetime import datetime

# BAD: Returning complex objects
@tool
def bad_get_time() -> datetime:
    """Get current time."""
    return datetime.now()  # datetime not JSON-serializable

# GOOD: Return strings or JSON
@tool
def good_get_time() -> str:
    """Get current time."""
    return datetime.now().isoformat()
```
