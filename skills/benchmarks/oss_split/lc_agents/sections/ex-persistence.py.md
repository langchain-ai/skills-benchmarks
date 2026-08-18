Persist state across conversations:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = create_agent(model="gpt-4.1", tools=[search], checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)

# Later conversation - agent remembers
result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Response: "Your name is Alice"
```
