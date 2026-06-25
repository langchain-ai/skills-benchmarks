Approve a pending tool call:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

# Step 1: Agent proposes write_file
result = agent.invoke({
    "messages": [{"role": "user", "content": "Write config to /prod.yaml"}]
}, config=config)

# Step 2: Get interrupts
state = agent.get_state(config)
interrupt = state.tasks[0]  # First interrupt

# Step 3: Approve
agent.update_state(
    config,
    {
        "messages": [
            Command(
                resume={
                    "decisions": [{"type": "approve"}]
                }
            )
        ]
    }
)

# Step 4: Continue execution
result = agent.invoke(None, config=config)
```
