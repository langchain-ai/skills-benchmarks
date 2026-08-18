Create minimal agent with defaults:

```python
from deepagents import create_deep_agent

# Minimal agent with default settings
agent = create_deep_agent()

# Invoke the agent
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What's the weather in Tokyo?"}
    ]
})
```
