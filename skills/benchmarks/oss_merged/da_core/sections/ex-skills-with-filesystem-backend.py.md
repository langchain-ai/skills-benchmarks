Set up an agent with skills directory and filesystem backend for on-demand skill loading.
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"],
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Use the python-testing skill"}]
}, config={"configurable": {"thread_id": "session-1"}})
```
