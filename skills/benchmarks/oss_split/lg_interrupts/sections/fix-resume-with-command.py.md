Use Command to resume:

```python
# WRONG - Passing regular dict
graph.invoke({"resume_data": "approve"}, config)  # Restarts!

# CORRECT - Use Command
from langgraph.types import Command
graph.invoke(Command(resume="approve"), config)
```
