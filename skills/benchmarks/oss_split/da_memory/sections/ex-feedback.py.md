Store feedback for later sessions:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_deep_agent(
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)}
    ),
    store=store
)

config = {"configurable": {"thread_id": "session-1"}}

# User provides feedback
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "I prefer FastAPI over Flask. Save this to /memories/preferences.txt"
    }]
}, config=config)

# Later session with different thread
config2 = {"configurable": {"thread_id": "session-2"}}
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Create a REST API for user management"
    }]
}, config=config2)
# Agent reads preferences and uses FastAPI
```
