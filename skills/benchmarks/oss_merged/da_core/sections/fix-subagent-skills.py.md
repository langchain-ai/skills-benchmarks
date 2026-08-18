Skills are not inherited by subagents - provide them explicitly.
```python
# WRONG: Custom subagents don't inherit skills
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# CORRECT: Provide skills explicitly
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", "skills": ["/helper-skills/"], ...}]
)
```
