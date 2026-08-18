Files are lost when thread changes:

```python
# Files lost when thread changes
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Write to /notes.txt"}]}, config=config1)

config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({"messages": [{"role": "user", "content": "Read /notes.txt"}]}, config=config2)
# File not found! Different thread

# Use same thread_id OR use StoreBackend for persistence
```
