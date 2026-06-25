Access store in custom tools:

```python
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

@tool
def get_user_preference(key: str, runtime: ToolRuntime) -> str:
    """Get a user preference from long-term storage."""
    store = runtime.store
    result = store.get(("user_prefs",), key)
    return str(result.value) if result else "Not found"

@tool
def save_user_preference(key: str, value: str, runtime: ToolRuntime) -> str:
    """Save a user preference to long-term storage."""
    store = runtime.store
    store.put(("user_prefs",), key, {"value": value})
    return f"Saved {key}={value}"

store = InMemoryStore()

agent = create_agent(
    model="gpt-4",
    tools=[get_user_preference, save_user_preference],
    store=store
)

# First session: save preference
agent.invoke({
    "messages": [{"role": "user", "content": "Remember I prefer dark mode"}]
})

# Second session: retrieve preference
agent.invoke({
    "messages": [{"role": "user", "content": "What UI theme do I prefer?"}]
})
```
