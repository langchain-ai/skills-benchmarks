---
name: langgraph-persistence-memory-py
description: "INVOKE THIS SKILL when your LangGraph needs to remember state across calls, use memory, or persist conversations. Covers checkpointers (MemorySaver, Postgres), thread_id configuration, and Store for long-term memory. CRITICAL: Fixes for missing thread_id, checkpointer placement, and cross-thread memory access."
---

<overview>
LangGraph's persistence layer enables durable execution by checkpointing graph state:

- **Checkpointer**: Saves/loads graph state at every super-step
- **Thread ID**: Identifies separate checkpoint sequences (conversations)
- **Store**: Cross-thread memory for user preferences, facts

**Two memory types:**
- **Short-term** (checkpointer): Thread-scoped conversation history
- **Long-term** (store): Cross-thread user preferences, facts
</overview>

<checkpointer-selection>

| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `InMemorySaver` | Testing, development | In-memory only | No |
| `SqliteSaver` | Local development | SQLite file | Partial (single-user) |
| `PostgresSaver` | Production | PostgreSQL | Yes |

</checkpointer-selection>

<memory-type-selection>

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| Short-term | Single thread | Via checkpointer | Conversation history |
| Long-term | Cross-thread | Via store | User preferences, facts |

</memory-type-selection>

---

## Checkpointer Setup

<ex-basic-persistence>
```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def add_message(state: State) -> dict:
    return {"messages": ["Bot response"]}

# Create checkpointer
checkpointer = InMemorySaver()

# Compile WITH checkpointer
graph = (
    StateGraph(State)
    .add_node("respond", add_message)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer)  # CRITICAL: Pass at compile time
)

# ALWAYS provide thread_id
config = {"configurable": {"thread_id": "conversation-1"}}

# First invocation
result1 = graph.invoke({"messages": ["Hello"]}, config)
print(len(result1["messages"]))  # 2

# Second invocation - state persisted!
result2 = graph.invoke({"messages": ["How are you?"]}, config)
print(len(result2["messages"]))  # 4 (previous + new)
```
</ex-basic-persistence>

<ex-production-postgres>
```python
from langgraph.checkpoint.postgres import PostgresSaver

# Use PostgreSQL for production (from_conn_string is a context manager in v3+)
with PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/db"
) as checkpointer:
    checkpointer.setup()  # only needed on first use to create tables
    graph = builder.compile(checkpointer=checkpointer)

# Async version
from langgraph.checkpoint.postgres import AsyncPostgresSaver

async def main():
    async with AsyncPostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/db"
    ) as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)
        result = await graph.ainvoke({"data": "test"}, config)
```
</ex-production-postgres>

---

## Thread Management

<ex-separate-threads>
```python
# Different threads maintain separate state
alice_config = {"configurable": {"thread_id": "user-alice"}}
bob_config = {"configurable": {"thread_id": "user-bob"}}

# Alice's conversation
graph.invoke({"messages": ["Hi from Alice"]}, alice_config)

# Bob's conversation (completely separate state)
graph.invoke({"messages": ["Hi from Bob"]}, bob_config)

# Alice's state is isolated from Bob's
```
</ex-separate-threads>

<ex-resume-from-checkpoint>
Time travel: browse checkpoint history and replay or fork from a past state.
```python
config = {"configurable": {"thread_id": "session-1"}}

result = graph.invoke({"messages": ["start"]}, config)

# Browse checkpoint history
states = list(graph.get_state_history(config))

# Replay from a past checkpoint
past = states[-2]
result = graph.invoke(None, past.config)  # None = resume from checkpoint

# Or fork: update state at a past checkpoint, then resume
fork_config = graph.update_state(past.config, {"messages": ["edited"]})
result = graph.invoke(None, fork_config)
```
</ex-resume-from-checkpoint>

<ex-update-state>
```python
# Modify state before resuming
config = {"configurable": {"thread_id": "session-1"}}

# Update state manually
graph.update_state(
    config,
    {"data": "manually_updated"}
)

# Resume with updated state
result = graph.invoke(None, config)
```
</ex-update-state>

---

## Long-Term Memory (Store)

<ex-long-term-memory-store>
```python
from langgraph.store.memory import InMemoryStore

# Create store for cross-thread memory
store = InMemoryStore()

# Save user preference (available across ALL threads)
user_id = "alice"
namespace = (user_id, "preferences")

store.put(
    namespace,
    "language",
    {"preference": "short, direct responses"}
)

# Node with store injection
def respond(state, *, store):
    """Store injected automatically when compiled with store."""
    user_id = state["user_id"]
    prefs = store.get((user_id, "preferences"), "language")
    return {"response": f"Using preference: {prefs}"}

# Compile with BOTH checkpointer and store
graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)

# Both threads access same long-term memory
thread1 = {"configurable": {"thread_id": "thread-1"}}
thread2 = {"configurable": {"thread_id": "thread-2"}}

graph.invoke({"user_id": "alice"}, thread1)  # Gets preferences
graph.invoke({"user_id": "alice"}, thread2)  # Same preferences!
```
</ex-long-term-memory-store>

<ex-store-operations>
```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Put (create/update)
store.put(
    ("user-123", "facts"),
    "location",
    {"city": "San Francisco"}
)

# Get
item = store.get(("user-123", "facts"), "location")

# Search with filters
results = store.search(
    ("user-123", "facts"),
    filter={"city": "San Francisco"}
)

# Delete
store.delete(("user-123", "facts"), "location")
```
</ex-store-operations>

<boundaries>
### What You CAN Configure

- Choose checkpointer implementation
- Specify thread IDs for conversation isolation
- Retrieve/update state at any checkpoint
- Set breakpoints for pausing
- Use stores for cross-thread memory
- Inject store into nodes

### What You CANNOT Configure

- Checkpoint timing (happens every super-step)
- Share short-term memory across threads
- Skip checkpointer for persistence features
</boundaries>

<fix-thread-id-required>
```python
# WRONG: No thread_id - state NOT persisted!
graph.invoke({"messages": ["Hello"]})
graph.invoke({"messages": ["What did I say?"]})  # Doesn't remember!

# CORRECT: Always provide thread_id
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"messages": ["Hello"]}, config)
graph.invoke({"messages": ["What did I say?"]}, config)  # Remembers!
```
</fix-thread-id-required>


<fix-inmemory-not-for-production>
```python
# WRONG: Data lost on process restart
checkpointer = InMemorySaver()  # In-memory only!
store = InMemoryStore()  # Also in-memory!

# CORRECT: Use persistent storage for production
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()  # only needed on first use to create tables
    store = PostgresStore.from_conn_string("postgresql://...")
    graph = builder.compile(checkpointer=checkpointer, store=store)
```
</fix-inmemory-not-for-production>

<fix-resume-with-none>
```python
# WRONG: Providing new input restarts from beginning
graph.invoke({"messages": ["New message"]}, config)  # Restarts!

# CORRECT: Use None to resume from checkpoint
graph.invoke(None, config)  # Continues from where it paused
```
</fix-resume-with-none>

<fix-update-state-with-reducers>
```python
from typing import Annotated
import operator
from langgraph.types import Overwrite

class State(TypedDict):
    items: Annotated[list, operator.add]

# Assume current state: {"items": ["A", "B"]}

# update_state PASSES THROUGH reducers
graph.update_state(config, {"items": ["C"]})
# Result: {"items": ["A", "B", "C"]}  # Appended!

# To REPLACE instead of append, use Overwrite
graph.update_state(config, {"items": Overwrite(["C"])})
# Result: {"items": ["C"]}  # Replaced
```
</fix-update-state-with-reducers>

<fix-store-injection>
```python
# WRONG: Store not available in node
def my_node(state):
    store.put(...)  # NameError! store not defined

# CORRECT: Inject store via keyword parameter
from langgraph.store.base import BaseStore

def my_node(state, *, store: BaseStore):
    store.put(...)  # Correct store instance injected
```
</fix-store-injection>
