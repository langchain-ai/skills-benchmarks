Specify destinations in type hint:

```python
# WRONG - No type hint for routing
def node_a(state) -> Command:
    return Command(goto="node_b")

# CORRECT - Specify possible destinations
from typing import Literal

def node_a(state) -> Command[Literal["node_b", "node_c"]]:
    return Command(goto="node_b")
```
