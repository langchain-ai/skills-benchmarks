Use FilesystemBackend for local skills:

```python
# Skills won't load without proper backend
agent = create_deep_agent(
    skills=["/path/to/skills/"]
)

# Use FilesystemBackend for local skills
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
