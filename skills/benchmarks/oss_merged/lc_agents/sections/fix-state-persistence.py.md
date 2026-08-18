Add checkpointer and thread_id to enable conversation memory.
```python
# WRONG: No checkpointer - each invoke is isolated
agent = create_agent(model="gpt-4.1", tools=[search])

# CORRECT
agent = create_agent(model="gpt-4.1", tools=[search], checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({"messages": [...]}, config=config)
```
