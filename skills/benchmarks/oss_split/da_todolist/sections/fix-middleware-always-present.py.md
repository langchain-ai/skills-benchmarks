Use create_agent for full control:

```python
# You cannot remove TodoListMiddleware from create_deep_agent
# It's part of the core harness

# This won't remove TodoList
from deepagents import create_deep_agent

agent = create_deep_agent(middleware=[])  # TodoList still included

# If you need full control, use create_agent from LangChain
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4",
    middleware=[]  # No middleware at all
)
```
