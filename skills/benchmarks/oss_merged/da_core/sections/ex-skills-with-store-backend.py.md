Load skill content into a Store backend for environments without filesystem access.
```python
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Load skill content into store
skill_content = """---
name: python-testing
description: Best practices for Python testing with pytest
---
# Python Testing Skill
..."""

store.put(
    namespace=("filesystem",),
    key="/skills/python-testing/SKILL.md",
    value=create_file_data(skill_content)
)

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=store,
    skills=["/skills/"]
)
```
