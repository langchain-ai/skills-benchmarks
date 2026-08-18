Configure agent with local skills:

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"],  # Path to skills directory
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "What is LangGraph? Use the langgraph-docs skill if available."
    }]
})
```
