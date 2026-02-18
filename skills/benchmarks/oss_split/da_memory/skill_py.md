---
name: Deep Agents Memory (Python)
description: [Deep Agents] Implementing long-term memory in Deep Agents with cross-session storage using StoreBackend, CompositeBackend, and InMemoryStore for persistent data.
---

# deepagents-memory (Python)

## Overview

Deep agents support two types of memory:

**Short-term (StateBackend)**: Persists within a single thread, lost when thread ends
**Long-term (StoreBackend)**: Persists across threads and sessions

Use **CompositeBackend** for hybrid storage: mix ephemeral and persistent files.

## Memory Types Comparison

| Type | Backend | Persistence | Use Case |
|------|---------|------------|----------|
| Short-term | StateBackend | Single thread | Temporary working files |
| Long-term | StoreBackend | Across threads | User preferences, learned patterns |
| Hybrid | CompositeBackend | Mix both | Some persistent, some temporary |

## Long-term Memory Setup

### Using CompositeBackend

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),  # Default for regular files
    routes={
        "/memories/": StoreBackend(rt),  # Persistent storage
    }
)

agent = create_deep_agent(
    backend=composite_backend,
    store=store
)

# Files with /memories/ prefix persist across threads
# Other files are ephemeral
```

### Path Routing

```python
# Ephemeral (StateBackend) - lost after thread ends
await agent.invoke({
    "messages": [{"role": "user", "content": "Write draft to /draft.txt"}]
})

# Persistent (StoreBackend) - survives across threads
await agent.invoke({
    "messages": [{"role": "user", "content": "Save preferences to /memories/prefs.txt"}]
})
```

## Code Examples

### Example 1: User Preferences Across Sessions

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

### Example 2: Learning from Feedback

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

### Example 3: Project Knowledge Base

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

### Example 4: Using Store Directly in Tools

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

## Decision Table: Memory Storage Patterns

| Pattern | Backend Setup | Use Case |
|---------|--------------|----------|
| All ephemeral | StateBackend | Single-session tasks |
| All persistent | StoreBackend | Everything remembered |
| Hybrid | CompositeBackend | `/memories/` persistent, rest ephemeral |
| Custom routing | CompositeBackend with multiple routes | Complex storage needs |

## Boundaries

### What Agents CAN Do
✅ Save files to persistent storage (/memories/)  
✅ Access persisted files across threads  
✅ Organize memory with custom paths  
✅ Mix ephemeral and persistent storage  
✅ Use Store namespace/key pattern directly

### What Agents CANNOT Do
❌ Access memory without proper Store setup  
❌ Share memory across different agents (without shared Store)  
❌ Persist files without StoreBackend configuration  
❌ Access StateBackend files across threads

## Gotchas

### 1. StoreBackend Requires Store Instance

```python
# ❌ Missing store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# ✅ Provide store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```

### 2. Path Prefix Matters for Routing

```python
# ❌ Won't be persistent (wrong path)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /prefs.txt"}]
})

# ✅ Persistent (matches /memories/ route)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /memories/prefs.txt"}]
})
```

### 3. InMemoryStore Not Persistent Across Process Restarts

```python
# ❌ InMemoryStore lost on restart
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()  # Lost when process ends

# ✅ Use PostgresStore for production
from langgraph.store.postgres import PostgresStore
store = PostgresStore(connection_string="postgresql://...")
```

### 4. CompositeBackend Routes Use Longest Prefix Match

```python
# Routes are matched by longest prefix
backend = CompositeBackend(
    default=StateBackend(rt),
    routes={
        "/mem/": StoreBackend(rt),
        "/mem/temp/": StateBackend(rt),  # More specific
    }
)

# /mem/file.txt -> StoreBackend
# /mem/temp/file.txt -> StateBackend (longer match)
# /workspace/file.txt -> StateBackend (default)
```

## Full Documentation

- [Long-term Memory Guide](https://docs.langchain.com/oss/python/deepagents/long-term-memory)
- [Backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [Memory Overview](https://docs.langchain.com/oss/python/concepts/memory)
- [LangGraph Store](https://docs.langchain.com/oss/python/langgraph/add-memory)
