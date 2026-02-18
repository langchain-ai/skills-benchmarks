---
name: Deep Agents Memory
description: [Deep Agents] Implementing long-term memory in Deep Agents with cross-session storage using StoreBackend, CompositeBackend, and InMemoryStore for persistent data.
---

<overview>
Deep agents support two types of memory:

**Short-term (StateBackend)**: Persists within a single thread, lost when thread ends
**Long-term (StoreBackend)**: Persists across threads and sessions

Use **CompositeBackend** for hybrid storage: mix ephemeral and persistent files.
</overview>

<memory-types-comparison>
| Type | Backend | Persistence | Use Case |
|------|---------|------------|----------|
| Short-term | StateBackend | Single thread | Temporary working files |
| Long-term | StoreBackend | Across threads | User preferences, learned patterns |
| Hybrid | CompositeBackend | Mix both | Some persistent, some temporary |
</memory-types-comparison>

<setup>
### Using CompositeBackend

<python>
Configure CompositeBackend with routes:

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
</python>

<typescript>
Configure CompositeBackend with routes:

```typescript
import { createDeepAgent, CompositeBackend, StateBackend, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = await createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    { "/memories/": new StoreBackend(config) }
  ),
  store
});

// /memories/* files persist across threads
// Other files are ephemeral
```
</typescript>

### Path Routing

<python>
Route files by path prefix:

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
</python>
</setup>

<ex-user-prefs>
<python>
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
</python>

<typescript>
Save and access preferences across threads:

```typescript
import { createDeepAgent, CompositeBackend, StateBackend, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = await createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    { "/memories/": new StoreBackend(config) }
  ),
  store
});

// Thread 1: Save preferences
const config1 = { configurable: { thread_id: "thread-1" } };
await agent.invoke({
  messages: [{
    role: "user",
    content: "Save my coding style to /memories/style.txt: TypeScript, async/await, Jest"
  }]
}, config1);

// Thread 2: Access preferences
const config2 = { configurable: { thread_id: "thread-2" } };
await agent.invoke({
  messages: [{
    role: "user",
    content: "Read my preferences and write a user fetch function"
  }]
}, config2);
// Agent reads /memories/style.txt
```
</typescript>
</ex-user-prefs>

<ex-feedback>
<python>
Store feedback for later sessions:

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
</python>
</ex-feedback>

<ex-knowledge-base>
<python>
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
</python>

<typescript>
Build persistent knowledge across sessions:

```typescript
const agent = await createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    {
      "/memories/": new StoreBackend(config),
      "/workspace/": new StateBackend(config),
    }
  ),
  store: new InMemoryStore()
});

// Build knowledge
await agent.invoke({
  messages: [{
    role: "user",
    content: "Document the DB schema in /memories/db-schema.md"
  }]
}, { configurable: { thread_id: "thread-1" } });

// Use knowledge later
await agent.invoke({
  messages: [{
    role: "user",
    content: "Write a migration to add email to users"
  }]
}, { configurable: { thread_id: "thread-2" } });
```
</typescript>
</ex-knowledge-base>

<ex-store-tools>
<python>
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
</python>

<typescript>
Access store in custom tools:

```typescript
import { tool } from "langchain";
import { createAgent } from "langchain";
import { InMemoryStore } from "@langchain/langgraph";
import { z } from "zod";

const getUserPreference = tool(
  async ({ key }) => {
    const value = await store.get(["user_prefs"], key);
    return value ? String(value) : "Not found";
  },
  {
    name: "get_user_preference",
    description: "Get a user preference",
    schema: z.object({ key: z.string() }),
  }
);

const saveUserPreference = tool(
  async ({ key, value }) => {
    await store.put(["user_prefs"], key, { value });
    return `Saved ${key}=${value}`;
  },
  {
    name: "save_user_preference",
    description: "Save a user preference",
    schema: z.object({ key: z.string(), value: z.string() }),
  }
);

const store = new InMemoryStore();

const agent = createAgent({
  model: "gpt-4",
  tools: [getUserPreference, saveUserPreference],
  store
});

// First session
await agent.invoke({
  messages: [{ role: "user", content: "Remember I prefer dark mode" }]
});

// Second session
await agent.invoke({
  messages: [{ role: "user", content: "What UI theme do I prefer?" }]
});
```
</typescript>
</ex-store-tools>

<decision-table>
| Pattern | Backend Setup | Use Case |
|---------|--------------|----------|
| All ephemeral | StateBackend | Single-session tasks |
| All persistent | StoreBackend | Everything remembered |
| Hybrid | CompositeBackend | `/memories/` persistent, rest ephemeral |
| Custom routing | CompositeBackend with multiple routes | Complex storage needs |
</decision-table>

<boundaries>
**What Agents CAN Do:**
- Save files to persistent storage (/memories/)
- Access persisted files across threads
- Organize memory with custom paths
- Mix ephemeral and persistent storage
- Use Store namespace/key pattern directly

**What Agents CANNOT Do:**
- Access memory without proper Store setup
- Share memory across different agents (without shared Store)
- Persist files without StoreBackend configuration
- Access StateBackend files across threads
</boundaries>

<fix-store-backend-requires-store>
<python>
Provide store when using StoreBackend:

```python
# Missing store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# Provide store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
</python>

<typescript>
Provide store when using StoreBackend:

```typescript
// Missing store
await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// Provide store
await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```
</typescript>
</fix-store-backend-requires-store>

<fix-path-prefix-routing>
<python>
Use correct path prefix for persistence:

```python
# Won't be persistent (wrong path)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /prefs.txt"}]
})

# Persistent (matches /memories/ route)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /memories/prefs.txt"}]
})
```
</python>

<typescript>
Use correct path prefix for persistence:

```typescript
// Not persistent (wrong path)
await agent.invoke({
  messages: [{ role: "user", content: "Save to /prefs.txt" }]
});

// Persistent (matches /memories/ route)
await agent.invoke({
  messages: [{ role: "user", content: "Save to /memories/prefs.txt" }]
});
```
</typescript>
</fix-path-prefix-routing>

<fix-inmemorystore-not-persistent>
<python>
Use PostgresStore for production:

```python
# InMemoryStore lost on restart
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()  # Lost when process ends

# Use PostgresStore for production
from langgraph.store.postgres import PostgresStore
store = PostgresStore(connection_string="postgresql://...")
```
</python>

<typescript>
Use PostgresStore for production:

```typescript
// Lost on restart
const store = new InMemoryStore();

// Use persistent store for production
import { PostgresStore } from "@langchain/langgraph";
const store = new PostgresStore({ connectionString: "postgresql://..." });
```
</typescript>
</fix-inmemorystore-not-persistent>

<fix-composite-backend-longest-prefix>
<python>
Longer prefixes take precedence:

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
</python>

<typescript>
Longer prefixes take precedence:

```typescript
const backend = (config) => new CompositeBackend(
  new StateBackend(config),
  {
    "/mem/": new StoreBackend(config),
    "/mem/temp/": new StateBackend(config),  // More specific
  }
);

// /mem/file.txt -> StoreBackend
// /mem/temp/file.txt -> StateBackend (longer match)
```
</typescript>
</fix-composite-backend-longest-prefix>

<links>
**Python:**
- [Long-term Memory Guide](https://docs.langchain.com/oss/python/deepagents/long-term-memory)
- [Backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [Memory Overview](https://docs.langchain.com/oss/python/concepts/memory)
- [LangGraph Store](https://docs.langchain.com/oss/python/langgraph/add-memory)

**TypeScript:**
- [Long-term Memory](https://docs.langchain.com/oss/javascript/deepagents/long-term-memory)
- [Backends](https://docs.langchain.com/oss/javascript/deepagents/backends)
- [Memory Overview](https://docs.langchain.com/oss/javascript/concepts/memory)
- [LangGraph Store](https://docs.langchain.com/oss/javascript/langgraph/add-memory)
</links>
