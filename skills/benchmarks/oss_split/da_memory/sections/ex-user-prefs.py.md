Save and access preferences across threads:

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

# Thread 1: Save preferences
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Save my coding style preferences to /memories/style.txt: use type hints, async/await, pytest"
    }]
}, config=config1)

# Thread 2: Access preferences (different thread!)
config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Read my coding preferences and write a function to fetch users"
    }]
}, config=config2)
# Agent reads /memories/style.txt and applies preferences
```
