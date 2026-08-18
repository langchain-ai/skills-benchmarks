Access the todo list from the agent's final state after invocation.
```python
result = agent.invoke({...}, config={"configurable": {"thread_id": "session-1"}})

# Access todo list from final state
todos = result.get("todos", [])
for todo in todos:
    print(f"[{todo['status']}] {todo['content']}")
```
