Create an agent with MemorySaver checkpointer for conversation persistence across invokes.
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)

result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Response: "Your name is Alice"
```
