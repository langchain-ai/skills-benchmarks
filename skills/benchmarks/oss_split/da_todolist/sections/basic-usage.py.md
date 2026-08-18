Agent uses write_todos for complex tasks:

```python
from deepagents import create_deep_agent

# TodoListMiddleware is included by default
agent = create_deep_agent()

# Agent will automatically use write_todos for complex tasks
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Create a Python web scraper that extracts product data from an e-commerce site, stores it in a database, and generates a report."
    }]
})
```
