Add reducer for list accumulation:

```python
# WRONG - List will be overwritten
class State(TypedDict):
    items: list  # No reducer!

# Node 1 returns: {"items": ["A"]}
# Node 2 returns: {"items": ["B"]}
# Final state: {"items": ["B"]}  # A is lost!

# CORRECT
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]
# Final state: {"items": ["A", "B"]}
```
