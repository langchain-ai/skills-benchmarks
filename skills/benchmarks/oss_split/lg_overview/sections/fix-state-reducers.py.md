Use reducers for list accumulation:

```python
# WRONG - Messages will be overwritten, not appended
class State(TypedDict):
    messages: list  # No reducer!

# CORRECT - Use reducer to append
from typing import Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]  # Appends messages
```
