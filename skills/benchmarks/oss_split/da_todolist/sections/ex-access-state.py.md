Read todos from final state:

```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Run the agent
result = agent.invoke(
    {
        "messages": [{
            "role": "user",
            "content": "Create a data processing pipeline"
        }]
    },
    config={"configurable": {"thread_id": "session-1"}}
)

# Access the todo list from the final state
todos = result.get("todos", [])
for todo in todos:
    print(f"[{todo['status']}] {todo['content']}")
```
