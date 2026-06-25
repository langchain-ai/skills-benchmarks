Create agent with default backend:

```python
from deepagents import create_deep_agent

# Default backend (StateBackend)
agent = create_deep_agent()

result = agent.invoke({
    "messages": [{"role": "user", "content": "Write notes to /draft.txt"}]
})
# File exists only within this thread
```
