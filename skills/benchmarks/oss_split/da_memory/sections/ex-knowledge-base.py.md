Build persistent knowledge across sessions:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_deep_agent(
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={
            "/memories/": StoreBackend(rt),  # Long-term
            "/workspace/": StateBackend(rt),  # Temporary
        }
    ),
    store=store
)

config = {"configurable": {"thread_id": "thread-1"}}

# Build project knowledge
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Document the database schema in /memories/db-schema.md"
    }]
}, config=config)

# Later, use that knowledge
config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Write a migration to add email field to users table"
    }]
}, config=config2)
# Agent reads /memories/db-schema.md for context
```
