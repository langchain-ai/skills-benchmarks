Updates pass through reducers:

```python
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]

# Assume current state: {"items": ["A", "B"]}

# update_state passes through reducers
graph.update_state(config, {"items": ["C"]})
# Result: {"items": ["A", "B", "C"]}  # Appended!

# To overwrite, use different approach
from langgraph.types import Overwrite
graph.update_state(config, {"items": Overwrite(["C"])})
# Result: {"items": ["C"]}  # Replaced
```
