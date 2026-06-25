Customize filesystem tool descriptions:

```python
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        FilesystemMiddleware(
            backend=None,  # Use default StateBackend
            system_prompt="Save intermediate results to /workspace/ directory",
            custom_tool_descriptions={
                "read_file": "Read files you've previously written. Use offset/limit for large files.",
                "write_file": "Save data to avoid context overflow. Organize in /workspace/.",
            }
        ),
    ],
)
```
