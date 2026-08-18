Cross-thread memory with store:

```python
from langgraph.store.memory import InMemoryStore

# Create store for long-term memory
store = InMemoryStore()

# Save user preference (available across all threads)
user_id = "alice"
namespace = (user_id, "preferences")

store.put(
    namespace,
    "language",
    {"preference": "short, direct responses"}
)

# Retrieve in any thread
def get_user_prefs(state, *, store):
    """Access store via dependency injection."""
    user_id = state["user_id"]
    namespace = (user_id, "preferences")

    prefs = store.get(namespace, "language")
    return {"preferences": prefs}

# Compile with store
graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)

# Use in different threads
thread1 = {"configurable": {"thread_id": "thread-1"}}
thread2 = {"configurable": {"thread_id": "thread-2"}}

# Both threads access same long-term memory
graph.invoke({"user_id": "alice"}, thread1)  # Gets preferences
graph.invoke({"user_id": "alice"}, thread2)  # Same preferences
```
