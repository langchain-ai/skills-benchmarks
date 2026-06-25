Provide checkpointer when using HITL:

```python
# This will error if interrupt_on is set
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# Checkpointer is required
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
