Agent skips planning for simple tasks:

```python
# The agent won't always use write_todos
# For simple tasks, it may skip planning

from deepagents import create_deep_agent

agent = create_deep_agent()

# Simple task - agent likely won't create todos
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is 2+2?"}]
})
# No todos in state

# Complex task - agent will likely create todos
result = agent.invoke({
    "messages": [{"role": "user", "content": "Build a web scraper and analyze the data"}]
})
# Todos present in state
```
