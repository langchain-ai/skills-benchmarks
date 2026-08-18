Invoke an agent that automatically creates a todo list for a multi-step task.
```python
from deepagents import create_deep_agent

agent = create_deep_agent()  # TodoListMiddleware included by default

result = agent.invoke({
    "messages": [{"role": "user", "content": "Create a REST API: design models, implement CRUD, add auth, write tests"}]
}, config={"configurable": {"thread_id": "session-1"}})

# Agent's planning via write_todos:
# [
#   {"content": "Design data models", "status": "in_progress"},
#   {"content": "Implement CRUD endpoints", "status": "pending"},
#   {"content": "Add authentication", "status": "pending"},
#   {"content": "Write tests", "status": "pending"}
# ]
```
