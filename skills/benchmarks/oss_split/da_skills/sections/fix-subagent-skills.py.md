Provide skills to subagents explicitly:

```python
# Main agent skills NOT inherited by custom subagents
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# Provide skills to subagent explicitly
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Explicit
        ...
    }]
)
```
