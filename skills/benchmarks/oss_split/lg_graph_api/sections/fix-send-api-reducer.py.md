Use reducer for parallel results:

```python
# WRONG - Results will be overwritten
class State(TypedDict):
    results: list  # No reducer!

# CORRECT - Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates results
```
