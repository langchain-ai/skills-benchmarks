Each agent has isolated state:

```python
# Subagents have their own todo lists
from deepagents import create_deep_agent

main_agent = create_deep_agent()
result = main_agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Use a subagent to process data"
    }]
})

# The subagent's todos are separate and won't appear in main_agent's state
```
