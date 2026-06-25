Update todos as requirements emerge:

```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Complex task where requirements emerge over time
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Debug why the application crashes on startup"
    }]
})

# Agent's evolving plan:
# Initial todos:
# [
#   {"content": "Reproduce the crash", "status": "in_progress"},
#   {"content": "Check error logs", "status": "pending"},
#   {"content": "Identify root cause", "status": "pending"}
# ]
#
# After investigation, agent updates:
# [
#   {"content": "Reproduce the crash", "status": "completed"},
#   {"content": "Check error logs", "status": "completed"},
#   {"content": "Identified missing environment variable", "status": "completed"},
#   {"content": "Add environment variable validation on startup", "status": "in_progress"},
#   {"content": "Update deployment documentation", "status": "pending"}
# ]
```
