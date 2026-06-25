Use Command class to resume execution after an interrupt.
```python
# WRONG
agent.invoke({"resume": {"decisions": [...]}})

# CORRECT
from langgraph.types import Command
agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
```
