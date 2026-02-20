---
name: Deep Agents Memory & Filesystem (TypeScript)
description: "INVOKE THIS SKILL when your Deep Agent needs memory, persistence, or filesystem access. Covers StateBackend (ephemeral), StoreBackend (persistent), FilesystemMiddleware, and CompositeBackend for routing. CRITICAL: Fixes for longest-prefix routing in CompositeBackend, path selection for persistence, and Store requirement."
---

<overview>
Deep Agents use pluggable backends for file operations and memory:

**Short-term (StateBackend)**: Persists within a single thread, lost when thread ends
**Long-term (StoreBackend)**: Persists across threads and sessions
**Hybrid (CompositeBackend)**: Route different paths to different backends

FilesystemMiddleware provides tools: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
</overview>

<backend-selection>

| Use Case | Backend | Why |
|----------|---------|-----|
| Temporary working files | StateBackend | Default, no setup |
| Local development CLI | FilesystemBackend | Direct disk access |
| Cross-session memory | StoreBackend | Persists across threads |
| Hybrid storage | CompositeBackend | Mix ephemeral + persistent |

</backend-selection>

<ex-default-state-backend>
Create an agent with the default StateBackend for ephemeral file storage.
```typescript
import { createDeepAgent } from "deepagents";

// Default backend (StateBackend) - files only exist within thread
const agent = await createDeepAgent();

const result = await agent.invoke({
  messages: [{ role: "user", content: "Write notes to /draft.txt" }]
}, { configurable: { thread_id: "thread-1" } });

// /draft.txt is lost when thread ends
```
</ex-default-state-backend>

<ex-composite-backend-for-hybrid>
Configure CompositeBackend to route paths to different storage backends.
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

// /draft.txt -> ephemeral (StateBackend)
// /memories/user-prefs.txt -> persistent (StoreBackend)
```
</ex-composite-backend-for-hybrid>

<ex-cross-session-memory>
Share files across different threads using StoreBackend for persistent paths.
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
  messages: [{ role: "user", content: "Save my coding style to /memories/style.txt" }]
}, config1);

// Thread 2: Access preferences (different thread!)
const config2 = { configurable: { thread_id: "thread-2" } };
await agent.invoke({
  messages: [{ role: "user", content: "Read my coding preferences" }]
}, config2);
// Agent reads /memories/style.txt
```
</ex-cross-session-memory>

<ex-filesystem-backend-local-dev>
Use FilesystemBackend for local development with real disk access and human-in-the-loop.
```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  interruptOn: { write_file: true, edit_file: true },
  checkpointer: new MemorySaver()
});
```

**Security: Never use FilesystemBackend in web servers - use StateBackend or sandbox instead.**
</ex-filesystem-backend-local-dev>

<boundaries>
### What Agents CAN Configure

- Backend type and configuration
- Routing rules for CompositeBackend
- Root directory for FilesystemBackend
- Human-in-the-loop for file operations

### What Agents CANNOT Configure

- Tool names (ls, read_file, write_file, edit_file, glob, grep)
- Access files outside virtual_mode restrictions
- Cross-thread file access without proper backend setup
</boundaries>

<fix-storebackend-requires-store>
Fix: StoreBackend requires a store instance to be provided.
```typescript
// WRONG: Missing store
const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// CORRECT: Provide store
import { InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```
</fix-storebackend-requires-store>

<fix-statebackend-files-dont-persist>
Fix: StateBackend files are thread-scoped and not shared across threads.
```typescript
// WRONG: Files lost when thread changes
const config1 = { configurable: { thread_id: "thread-1" } };
await agent.invoke({ messages: [{ role: "user", content: "Write to /notes.txt" }] }, config1);

const config2 = { configurable: { thread_id: "thread-2" } };
await agent.invoke({ messages: [{ role: "user", content: "Read /notes.txt" }] }, config2);
// File not found! Different thread

// CORRECT: Use same thread_id OR use StoreBackend for persistence
```
</fix-statebackend-files-dont-persist>

<fix-path-prefix-for-persistence>
Fix: Use the correct path prefix to match CompositeBackend routing rules.
```typescript
// With CompositeBackend routing /memories/ to StoreBackend:

// WRONG: Won't be persistent (wrong path)
await agent.invoke({ messages: [{ role: "user", content: "Save to /prefs.txt" }] });

// CORRECT: Persistent (matches /memories/ route)
await agent.invoke({ messages: [{ role: "user", content: "Save to /memories/prefs.txt" }] });
```
</fix-path-prefix-for-persistence>

<fix-production-store>
Fix: Use PostgresStore instead of InMemoryStore for production persistence.
```typescript
// WRONG: InMemoryStore lost on restart
import { InMemoryStore } from "@langchain/langgraph";
const store = new InMemoryStore();

// CORRECT: Use PostgresStore for production
import { PostgresStore } from "@langchain/langgraph";
const store = new PostgresStore({ connectionString: "postgresql://..." });
```
</fix-production-store>
