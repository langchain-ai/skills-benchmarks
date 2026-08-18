Use `Command(resume={...})` (Python) or `new Command({ resume: {...} })` (TypeScript), not a plain dict/object.

Use Command class to resume.

```python
# Problem: Wrong resume format
agent.invoke({"resume": {"decisions": [...]}})  # Wrong!

# Solution: Use Command
from langgraph.types import Command

agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
```
