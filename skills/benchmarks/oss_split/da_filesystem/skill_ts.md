---
name: Deep Agents Filesystem (TypeScript)
description: [Deep Agents] Using FilesystemMiddleware with virtual filesystems, backends (State, Store, Filesystem, Composite), and context management for Deep Agents.
---

# deepagents-filesystem (JavaScript/TypeScript)

## Overview

FilesystemMiddleware solves context engineering challenges by providing file operations through a pluggable backend system. Tools include: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`.

## Backend Types

### StateBackend (Default)
Ephemeral storage in agent state - persists within a thread only.

```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({});
// Default StateBackend - files exist only within thread
```

### FilesystemBackend (Local Disk)
```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({
    rootDir: ".",
    virtualMode: true  // Security: restrict paths
  })
});
```

### StoreBackend (Persistent)
```typescript
import { createDeepAgent, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store
});
```

### CompositeBackend (Hybrid)
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
```

## Decision Table

| Use Case | Backend | Why |
|----------|---------|-----|
| Temporary files | StateBackend | Default, no setup |
| Local development | FilesystemBackend | Direct disk access |
| Cross-session memory | StoreBackend | Persists across threads |
| Hybrid storage | CompositeBackend | Mix ephemeral + persistent |

## Code Examples

### Example 1: Managing Large Context
```typescript
const agent = await createDeepAgent({});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Search for TypeScript best practices and save results for analysis"
  }]
});
// Agent: search -> write_file -> compact context -> read_file when needed
```

### Example 2: Long-term Memory
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
await agent.invoke({
  messages: [{ role: "user", content: "Save my preference: concise explanations to /memories/prefs.txt" }]
}, { configurable: { thread_id: "thread-1" } });

// Thread 2: Access preferences
await agent.invoke({
  messages: [{ role: "user", content: "Read my preferences and explain async/await" }]
}, { configurable: { thread_id: "thread-2" } });
```

### Example 3: Custom Tool Descriptions
```typescript
import { createAgent, createFilesystemMiddleware } from "langchain";

const agent = createAgent({
  model: "claude-sonnet-4-5-20250929",
  middleware: [
    createFilesystemMiddleware({
      systemPrompt: "Save intermediate results to /workspace/",
      customToolDescriptions: {
        read_file: "Read files you've previously written. Use offset/limit for large files.",
        write_file: "Save data to avoid context overflow.",
      }
    }),
  ],
});
```

## Boundaries

### What Agents CAN Configure
✅ Backend type and configuration  
✅ Custom tool descriptions  
✅ File paths and organization  
✅ Human-in-the-loop for file operations

### What Agents CANNOT Configure
❌ Tool names  
❌ Disable filesystem tools  
❌ Access outside virtual_mode restrictions  

## Gotchas

### 1. StateBackend Files Don't Persist Across Threads
```typescript
// ❌ Files lost when thread changes
await agent.invoke({messages: [{role: "user", content: "Write /notes.txt"}]}, 
  {configurable: {thread_id: "thread-1"}});
await agent.invoke({messages: [{role: "user", content: "Read /notes.txt"}]}, 
  {configurable: {thread_id: "thread-2"}});
// File not found!

// ✅ Use same thread_id OR StoreBackend
```

### 2. FilesystemBackend Security
```typescript
// ❌ Insecure
new FilesystemBackend({ rootDir: "/project", virtualMode: false })

// ✅ Secure
new FilesystemBackend({ rootDir: "/project", virtualMode: true })
```

### 3. StoreBackend Requires Store
```typescript
// ❌ Missing store
await createDeepAgent({ backend: (config) => new StoreBackend(config) });

// ✅ Provide store
await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```

## Full Documentation
- [Filesystem Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#filesystem-middleware)
- [Backends Guide](https://docs.langchain.com/oss/javascript/deepagents/backends)
- [Long-term Memory](https://docs.langchain.com/oss/javascript/deepagents/long-term-memory)
