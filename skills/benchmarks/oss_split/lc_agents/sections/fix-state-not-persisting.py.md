Add checkpointer for conversation memory:

```python
# Problem: No checkpointer
agent = create_agent(model="gpt-4.1", tools=[search])

# Each invoke is isolated - no memory
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember "Bob"

# Solution: Add checkpointer and thread_id
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Bob"
```
