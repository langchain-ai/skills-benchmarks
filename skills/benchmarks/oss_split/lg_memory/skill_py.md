---
name: LangGraph Memory (Python)
description: "[LangGraph] Memory in LangGraph: short-term (thread-scoped) vs long-term (cross-thread) memory using checkpointers and stores"
---

# langgraph-memory (Python)


## Overview

LangGraph provides two types of memory for agents:
- **Short-term memory**: Thread-scoped, managed via checkpointers
- **Long-term memory**: Cross-thread, managed via stores

## Decision Table: Memory Types

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| Short-term | Single thread | Via checkpointer | Conversation history |
| Long-term | Cross-thread | Via store | User preferences, facts |

## Code Examples

### Short-Term Memory (Thread-Scoped)

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def respond(state):
    # Access conversation history
    history = state["messages"]
    return {"messages": [f"I remember {len(history)} messages"]}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("respond", respond)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer)
)

# First turn
config = {"configurable": {"thread_id": "user-1"}}
graph.invoke({"messages": ["Hello"]}, config)

# Second turn - remembers first
graph.invoke({"messages": ["How are you?"]}, config)
# Response: "I remember 3 messages" (Hello, response, How are you?)
```

### Long-Term Memory (Cross-Thread)

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

### Store Operations

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Put (create/update)
store.put(
    ("user-123", "facts"),
    "location",
    {"city": "San Francisco", "country": "USA"}
)

# Get
item = store.get(("user-123", "facts"), "location")
print(item)  # {'city': 'San Francisco', 'country': 'USA'}

# Search with filters
results = store.search(
    ("user-123", "facts"),
    filter={"country": "USA"}
)

# Delete
store.delete(("user-123", "facts"), "location")
```

### Accessing Store in Nodes

```python
from langgraph.store.base import BaseStore

def my_node(state, *, store: BaseStore):
    """Store injected automatically."""
    namespace = (state["user_id"], "memories")
    
    # Retrieve past memories
    memories = store.search(namespace, query="preferences")
    
    # Save new memory
    store.put(
        namespace,
        "new_fact",
        {"fact": "User likes Python"}
    )
    
    return {"processed": True}

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
```

### Combining Short and Long-Term Memory

```python
def smart_node(state, *, store):
    # Short-term: conversation context
    recent_messages = state["messages"][-5:]  # Last 5 messages
    
    # Long-term: user profile
    user_id = state["user_id"]
    profile = store.get((user_id, "profile"), "info")
    
    # Use both for personalized response
    response = generate_response(recent_messages, profile)
    
    return {"messages": [response]}

graph = (
    StateGraph(State)
    .add_node("respond", smart_node)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer, store=store)
)
```

### Persistent Stores (Production)

```python
from langgraph.store.postgres import PostgresStore

# Use PostgreSQL for production
store = PostgresStore.from_conn_string(
    "postgresql://user:pass@localhost/db"
)

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
```

## Boundaries

### What You CAN Configure

✅ Use checkpointers for short-term memory
✅ Use stores for long-term memory
✅ Namespace organization
✅ Search and filter memories
✅ Inject store into nodes
✅ Choose store backend

### What You CANNOT Configure

❌ Share short-term memory across threads
❌ Modify memory serialization format
❌ Store mechanism internals

## Gotchas

### 1. Short-Term Needs Checkpointer

```python
# ❌ WRONG - No checkpointer, no memory
graph = builder.compile()  # Messages lost!

# ✅ CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

### 2. Long-Term Needs Store

```python
# ❌ WRONG - Trying to share data without store
# Can't access data from other threads with checkpointer alone!

# ✅ CORRECT - Use store
store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```

### 3. Store Must Be Injected

```python
# ❌ WRONG - Store not available
def my_node(state):
    store.put(...)  # NameError or wrong store!

# ✅ CORRECT - Inject via parameter
def my_node(state, *, store: BaseStore):
    store.put(...)  # Correct store instance
```

### 4. InMemoryStore Not for Production

```python
# ❌ WRONG - Data lost on restart
store = InMemoryStore()  # Memory only!

# ✅ CORRECT - Use persistent backend
from langgraph.store.postgres import PostgresStore
store = PostgresStore.from_conn_string("postgresql://...")
```

## Links

- [Memory Overview](https://docs.langchain.com/oss/python/concepts/memory)
- [Short-Term Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Long-Term Memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [Store Reference](https://docs.langchain.com/oss/python/langgraph/persistence#memory-store)
