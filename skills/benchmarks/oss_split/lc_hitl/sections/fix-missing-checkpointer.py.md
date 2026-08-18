HITL requires a checkpointer - always add `MemorySaver()` or another persistence backend.

Add checkpointer to enable HITL.

```python
# Problem: No checkpointer
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    middleware=[HumanInTheLoopMiddleware({...})],  # Error!
)

# Solution: Always add checkpointer
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required
    middleware=[HumanInTheLoopMiddleware({...})],
)
```
