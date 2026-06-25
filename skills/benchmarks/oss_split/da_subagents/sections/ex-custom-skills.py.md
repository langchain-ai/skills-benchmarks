Provide skills explicitly to subagent:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    skills=["/main-skills/"],  # Main agent skills
    subagents=[
        {
            "name": "python-expert",
            "description": "Python code review and refactoring",
            "system_prompt": "Review Python code for best practices",
            "tools": [read_code, suggest_improvements],
            "skills": ["/python-skills/"],  # Subagent-specific skills
        }
    ]
)
# Note: Custom subagents DON'T inherit main agent's skills by default
# General-purpose subagent DOES inherit main agent's skills
```
