Provide skills to subagent explicitly:

```python
# Subagent won't have main agent's skills
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# Explicitly provide skills to subagent
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Subagent-specific
        ...
    }]
)

# General-purpose subagent DOES inherit main skills
# agent.invoke() -> task(instruction="...") uses general-purpose with main skills
```
