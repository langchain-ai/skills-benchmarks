Read actual project files with HITL safety:

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(
        root_dir="/Users/username/project",
        virtual_mode=True
    ),
    interrupt_on={"write_file": True, "edit_file": True}  # Safety
)

# Agent can read actual project files
result = agent.invoke({
    "messages": [{"role": "user", "content": "Analyze the code in src/main.py"}]
})
```
