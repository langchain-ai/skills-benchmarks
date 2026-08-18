Seed state with skill files:

```python
from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

# Prepare skill content
skill_content = """---
name: python-testing
description: Best practices for Python testing with pytest
---
# Python Testing Skill
..."""

skills_files = {
    "/skills/python-testing/SKILL.md": create_file_data(skill_content)
}

agent = create_deep_agent(
    skills=["/skills/"],
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "How should I write tests?"
    }],
    "files": skills_files  # Seed state with skill files
})
```
