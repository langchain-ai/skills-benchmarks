Access saved preferences across threads:

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

# Thread 1: Save user preferences
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({
    "messages": [{"role": "user", "content": "Save my preference: I like concise explanations to /memories/prefs.txt"}]
}, config=config1)

# Thread 2: Access saved preferences
config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({
    "messages": [{"role": "user", "content": "Read my preferences and explain asyncio"}]
}, config=config2)
# Agent reads /memories/prefs.txt and provides concise explanation
```
