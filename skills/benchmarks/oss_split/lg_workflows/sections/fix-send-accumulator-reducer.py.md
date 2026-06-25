Use reducer to collect worker results:

```python
# WRONG - Last worker overwrites all others
class State(TypedDict):
    results: list  # No reducer!

# CORRECT - Use Annotated with operator.add
from typing import Annotated
import operator

class State(TypedDict):
    results: Annotated[list, operator.add]  # Accumulates
```
