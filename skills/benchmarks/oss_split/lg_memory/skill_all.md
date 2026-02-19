---
name: LangGraph Memory
description: "[LangGraph] Memory in LangGraph: short-term (thread-scoped) vs long-term (cross-thread) memory using checkpointers and stores"
---

<overview>
LangGraph provides two types of memory for agents:
- **Short-term memory**: Thread-scoped, managed via checkpointers
- **Long-term memory**: Cross-thread, managed via stores
</overview>

<decision-table>

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| Short-term | Single thread | Via checkpointer | Conversation history |
| Long-term | Cross-thread | Via store | User preferences, facts |

</decision-table>

<ex-short-term>
<python>
Thread-scoped memory with checkpointer:

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
</python>

<typescript>
Thread-scoped memory with checkpointer:

```typescript
import { MemorySaver, StateGraph, StateSchema, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  messages: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});

const respond = async (state: typeof State.State) => {
  // Access conversation history
  const history = state.messages;
  return { messages: [`I remember ${history.length} messages`] };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("respond", respond)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });

// First turn
const config = { configurable: { thread_id: "user-1" } };
await graph.invoke({ messages: ["Hello"] }, config);

// Second turn - remembers first
await graph.invoke({ messages: ["How are you?"] }, config);
// Response: "I remember 3 messages" (Hello, response, How are you?)
```
</typescript>
</ex-short-term>

<ex-long-term>
<python>
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
</python>

<typescript>
Cross-thread memory with store:

```typescript
import { InMemoryStore } from "@langchain/langgraph";

// Create store for long-term memory
const store = new InMemoryStore();

// Save user preference (available across all threads)
const userId = "alice";
const namespace = [userId, "preferences"];

await store.put(
  namespace,
  "language",
  { preference: "short, direct responses" }
);

// Retrieve in any thread
const getUserPrefs = async (state, config) => {
  const store = config.store;
  const userId = state.userId;
  const namespace = [userId, "preferences"];

  const prefs = await store.get(namespace, "language");
  return { preferences: prefs };
};

// Compile with store
const graph = builder.compile({
  checkpointer,
  store,
});

// Use in different threads
const thread1 = { configurable: { thread_id: "thread-1" } };
const thread2 = { configurable: { thread_id: "thread-2" } };

// Both threads access same long-term memory
await graph.invoke({ userId: "alice" }, thread1);  // Gets preferences
await graph.invoke({ userId: "alice" }, thread2);  // Same preferences
```
</typescript>
</ex-long-term>

<ex-store-ops>
<python>
Basic store CRUD operations:

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
</python>

<typescript>
Basic store CRUD operations:

```typescript
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

// Put (create/update)
await store.put(
  ["user-123", "facts"],
  "location",
  { city: "San Francisco", country: "USA" }
);

// Get
const item = await store.get(["user-123", "facts"], "location");
console.log(item);  // { city: 'San Francisco', country: 'USA' }

// Search with filters
const results = await store.search(
  ["user-123", "facts"],
  { filter: { country: "USA" } }
);

// Delete
await store.delete(["user-123", "facts"], "location");
```
</typescript>
</ex-store-ops>

<ex-store-nodes>
<python>
Inject store via parameter:

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
</python>

<typescript>
Access store via config:

```typescript
import { BaseStore } from "@langchain/langgraph";

const myNode = async (state, config: { store: BaseStore }) => {
  const store = config.store;
  const namespace = [state.userId, "memories"];

  // Retrieve past memories
  const memories = await store.search(namespace, { query: "preferences" });

  // Save new memory
  await store.put(
    namespace,
    "new_fact",
    { fact: "User likes TypeScript" }
  );

  return { processed: true };
};

const graph = builder.compile({
  checkpointer,
  store,
});
```
</typescript>
</ex-store-nodes>

<ex-combined>
<python>
Use both memory types together:

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
</python>

<typescript>
Use both memory types together:

```typescript
const smartNode = async (state, config) => {
  const store = config.store;

  // Short-term: conversation context
  const recentMessages = state.messages.slice(-5);  // Last 5 messages

  // Long-term: user profile
  const userId = state.userId;
  const profile = await store.get([userId, "profile"], "info");

  // Use both for personalized response
  const response = await generateResponse(recentMessages, profile);

  return { messages: [response] };
};

const graph = new StateGraph(State)
  .addNode("respond", smartNode)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer, store });
```
</typescript>
</ex-combined>

<ex-persistent>
<python>
PostgreSQL for production:

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
</python>

<typescript>
PostgreSQL for production:

```typescript
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres";

// Use PostgreSQL for production
const store = await PostgresStore.fromConnString(
  "postgresql://user:pass@localhost/db"
);

const graph = builder.compile({
  checkpointer,
  store,
});
```
</typescript>
</ex-persistent>

<boundaries>
**What You CAN Configure**

- Use checkpointers for short-term memory
- Use stores for long-term memory
- Namespace organization
- Search and filter memories
- Inject store into nodes (Python) / Access store via config (TypeScript)
- Choose store backend

**What You CANNOT Configure**

- Share short-term memory across threads
- Modify memory serialization format
- Store mechanism internals
</boundaries>

<fix-short-term-needs-checkpointer>
<python>
Add checkpointer for short-term memory:

```python
# WRONG - No checkpointer, no memory
graph = builder.compile()  # Messages lost!

# CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```
</python>

<typescript>
Add checkpointer for short-term memory:

```typescript
// WRONG - No checkpointer, no memory
const graph = builder.compile();  // Messages lost!

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```
</typescript>
</fix-short-term-needs-checkpointer>

<fix-long-term-needs-store>
<python>
Add store for cross-thread memory:

```python
# WRONG - Trying to share data without store
# Can't access data from other threads with checkpointer alone!

# CORRECT - Use store
store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```
</python>

<typescript>
Add store for cross-thread memory:

```typescript
// WRONG - Trying to share data without store
// Can't access data from other threads with checkpointer alone!

// CORRECT - Use store
const store = new InMemoryStore();
const graph = builder.compile({ checkpointer, store });
```
</typescript>
</fix-long-term-needs-store>

<fix-store-injection>
<python>
Inject store via parameter:

```python
# WRONG - Store not available
def my_node(state):
    store.put(...)  # NameError or wrong store!

# CORRECT - Inject via parameter
def my_node(state, *, store: BaseStore):
    store.put(...)  # Correct store instance
```
</python>

<typescript>
Access store via config:

```typescript
// WRONG - Store not available
const myNode = async (state) => {
  store.put(...);  // ReferenceError!
};

// CORRECT - Access via config
const myNode = async (state, config) => {
  const store = config.store;
  await store.put(...);
};
```
</typescript>
</fix-store-injection>

<fix-inmemorystore-not-for-production>
<python>
Use persistent backend in production:

```python
# WRONG - Data lost on restart
store = InMemoryStore()  # Memory only!

# CORRECT - Use persistent backend
from langgraph.store.postgres import PostgresStore
store = PostgresStore.from_conn_string("postgresql://...")
```
</python>

<typescript>
Use persistent backend in production:

```typescript
// WRONG - Data lost on restart
const store = new InMemoryStore();  // Memory only!

// CORRECT - Use persistent backend
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres";
const store = await PostgresStore.fromConnString("postgresql://...");
```
</typescript>
</fix-inmemorystore-not-for-production>

<fix-await-store-operations>
<typescript>
Await async store operations:

```typescript
// WRONG
const item = store.get(namespace, key);
console.log(item);  // Promise!

// CORRECT
const item = await store.get(namespace, key);
console.log(item);
```
</typescript>
</fix-await-store-operations>

<links>
**Python**
- [Memory Overview](https://docs.langchain.com/oss/python/concepts/memory)
- [Short-Term Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Long-Term Memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [Store Reference](https://docs.langchain.com/oss/python/langgraph/persistence#memory-store)

**TypeScript**
- [Memory Overview](https://docs.langchain.com/oss/javascript/concepts/memory)
- [Short-Term Memory](https://docs.langchain.com/oss/javascript/langchain/short-term-memory)
- [Long-Term Memory](https://docs.langchain.com/oss/javascript/langchain/long-term-memory)
- [Store Reference](https://docs.langchain.com/oss/javascript/langgraph/persistence#memory-store)
</links>
