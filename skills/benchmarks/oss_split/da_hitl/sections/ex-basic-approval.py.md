Invoke and check for interrupts:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)

# Initial invocation
config = {"configurable": {"thread_id": "session-1"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "Write deployment config to /config/prod.yaml"}]
}, config=config)

# Execution pauses - check for interrupts
state = agent.get_state(config)
if state.next:  # Has interrupts
    for interrupt in state.tasks:
        print(f"Interrupt: {interrupt}")
```
