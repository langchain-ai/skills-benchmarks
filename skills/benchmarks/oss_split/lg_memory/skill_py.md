---
name: LangGraph Memory (Python)
description: "[LangGraph] Memory in LangGraph: short-term (thread-scoped) vs long-term (cross-thread) memory using checkpointers and stores"
---

<overview>
LangGraph provides two types of memory for agents:
- **Short-term memory**: Thread-scoped, managed via checkpointers
- **Long-term memory**: Cross-thread, managed via stores
</overview>

<memory-type-selection>

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| Short-term | Single thread | Via checkpointer | Conversation history |
| Long-term | Cross-thread | Via store | User preferences, facts |

</memory-type-selection>

<ex-short-term-memory>
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
</ex-short-term-memory>

<ex-long-term-memory>
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
</ex-long-term-memory>

<ex-store-operations>
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
</ex-store-operations>

<ex-store-in-nodes>
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
</ex-store-in-nodes>

<ex-combining-memory-types>
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
</ex-combining-memory-types>

<ex-postgres-store>
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
</ex-postgres-store>

<boundaries>
### What You CAN Configure

- Use checkpointers for short-term memory
- Use stores for long-term memory
- Namespace organization
- Search and filter memories
- Inject store into nodes
- Choose store backend

### What You CANNOT Configure

- Share short-term memory across threads
- Modify memory serialization format
- Store mechanism internals
</boundaries>

<fix-checkpointer-required>
```python
# WRONG: WRONG - No checkpointer, no memory
graph = builder.compile()  # Messages lost!

# CORRECT: CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```
</fix-checkpointer-required>

<fix-store-required>
```python
# WRONG: WRONG - Trying to share data without store
# Can't access data from other threads with checkpointer alone!

# CORRECT: CORRECT - Use store
store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```
</fix-store-required>

<fix-store-injection>
```python
# WRONG: WRONG - Store not available
def my_node(state):
    store.put(...)  # NameError or wrong store!

# CORRECT: CORRECT - Inject via parameter
def my_node(state, *, store: BaseStore):
    store.put(...)  # Correct store instance
```
</fix-store-injection>

<fix-production-store>
```python
# WRONG: WRONG - Data lost on restart
store = InMemoryStore()  # Memory only!

# CORRECT: CORRECT - Use persistent backend
from langgraph.store.postgres import PostgresStore
store = PostgresStore.from_conn_string("postgresql://...")
```
</fix-production-store>

<links>
- [Memory Overview](https://docs.langchain.com/oss/python/concepts/memory)
- [Short-Term Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Long-Term Memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [Store Reference](https://docs.langchain.com/oss/python/langgraph/persistence#memory-store)
</links>
