Invoke agent, check interrupt, then approve.

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "session-1"}}

# Step 1: Agent runs until it needs to call tool
result1 = agent.invoke({
    "messages": [{"role": "user", "content": "Send email to john@example.com saying hello"}]
}, config=config)

# Check for interrupt
if "__interrupt__" in result1:
    interrupt = result1["__interrupt__"][0]
    print(f"Waiting for approval: {interrupt.value}")

# Step 2: Human approves
result2 = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
print(result2["messages"][-1].content)
```
