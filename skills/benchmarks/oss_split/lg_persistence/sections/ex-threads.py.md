Isolated state per thread:

```python
# Different threads maintain separate state
thread1_config = {"configurable": {"thread_id": "user-alice"}}
thread2_config = {"configurable": {"thread_id": "user-bob"}}

# Alice's conversation
graph.invoke({"messages": ["Hi from Alice"]}, thread1_config)

# Bob's conversation (separate state)
graph.invoke({"messages": ["Hi from Bob"]}, thread2_config)

# Alice's state is isolated from Bob's
```
