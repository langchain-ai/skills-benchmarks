---
name: Deep Agents Memory (TypeScript)
description: [Deep Agents] Implementing long-term memory in Deep Agents with cross-session storage using StoreBackend, CompositeBackend, and InMemoryStore for persistent data.
---

# deepagents-memory (JavaScript/TypeScript)

## Overview

**Short-term (StateBackend)**: Single thread only  
**Long-term (StoreBackend)**: Persists across threads  
**Hybrid (CompositeBackend)**: Mix both

## Long-term Memory Setup

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

## Code Examples

### Example 1: User Preferences Across Sessions

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

### Example 2: Using Store Directly in Tools

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

### Example 3: Project Knowledge Base

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

## Decision Table

| Pattern | Backend | Use Case |
|---------|---------|----------|
| All ephemeral | StateBackend | Single-session tasks |
| All persistent | StoreBackend | Everything remembered |
| Hybrid | CompositeBackend | `/memories/` persistent, rest ephemeral |

## Boundaries

### What Agents CAN Do
✅ Save files to persistent storage  
✅ Access persisted files across threads  
✅ Mix ephemeral and persistent storage  
✅ Use Store namespace/key pattern

### What Agents CANNOT Do
❌ Access memory without Store  
❌ Persist StateBackend files across threads  
❌ Share memory across agents without shared Store

## Gotchas

### 1. StoreBackend Requires Store

```typescript
// ❌ Missing store
await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// ✅ Provide store
await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```

### 2. Path Prefix Matters

```typescript
// ❌ Not persistent (wrong path)
await agent.invoke({
  messages: [{ role: "user", content: "Save to /prefs.txt" }]
});

// ✅ Persistent (matches /memories/ route)
await agent.invoke({
  messages: [{ role: "user", content: "Save to /memories/prefs.txt" }]
});
```

### 3. InMemoryStore Not Persistent

```typescript
// ❌ Lost on restart
const store = new InMemoryStore();

// ✅ Use persistent store for production
import { PostgresStore } from "@langchain/langgraph";
const store = new PostgresStore({ connectionString: "postgresql://..." });
```

### 4. Routes Use Longest Prefix Match

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

## Full Documentation

- [Long-term Memory](https://docs.langchain.com/oss/javascript/deepagents/long-term-memory)
- [Backends](https://docs.langchain.com/oss/javascript/deepagents/backends)
- [Memory Overview](https://docs.langchain.com/oss/javascript/concepts/memory)
- [LangGraph Store](https://docs.langchain.com/oss/javascript/langgraph/add-memory)
