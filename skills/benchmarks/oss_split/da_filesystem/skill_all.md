---
name: Deep Agents Filesystem
description: [Deep Agents] Using FilesystemMiddleware with virtual filesystems, backends (State, Store, Filesystem, Composite), and context management for Deep Agents.
---

## Overview

FilesystemMiddleware solves context engineering challenges by providing file operations through a pluggable backend system. It allows agents to offload large context to filesystem storage, preventing context window overflow.

**Built-in Filesystem Tools:**
- `ls` - List files in a directory
- `read_file` - Read entire files or specific line ranges
- `write_file` - Create new files
- `edit_file` - Edit existing files with exact string replacement
- `glob` - Find files matching patterns
- `grep` - Search for text across files

## When to Use Filesystem Middleware

| Use Filesystem Tools When | Alternative Approach |
|--------------------------|---------------------|
| Tool results are variable-length (web_search, RAG) | Keep in message history (if small) |
| Working with large documents or code | Use specialized tools |
| Need persistent storage across turns | Use short-term message history |
| Multiple files need coordination | Single-turn operations |

## Backend Types

### StateBackend (Default)

Ephemeral storage in agent state - persists within a thread only.

#### Python

```python
from deepagents import create_deep_agent

# Default backend (StateBackend)
agent = create_deep_agent()

result = agent.invoke({
    "messages": [{"role": "user", "content": "Write notes to /draft.txt"}]
})
# File exists only within this thread
```

#### TypeScript

```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({});
// Default StateBackend - files exist only within thread
```

### FilesystemBackend (Local Disk)

Direct access to local filesystem.

#### Python

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(
        root_dir=".",  # Root directory
        virtual_mode=True  # Enable path restrictions
    )
)

# Agent can now read/write to actual files on disk
result = agent.invoke({
    "messages": [{"role": "user", "content": "Read the README.md file"}]
})
```

#### TypeScript

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({
    rootDir: ".",
    virtualMode: true  // Security: restrict paths
  })
});
```

**Security Considerations:**
- Use `virtual_mode=True` (Python) / `virtualMode: true` (TypeScript) to prevent `..`, `~`, and absolute path access
- Enable Human-in-the-Loop for sensitive operations
- Never use in web servers - use StateBackend or sandbox instead
- Secrets (API keys, .env) are readable by the agent

### StoreBackend (Persistent Cross-Thread)

Storage that persists across threads using LangGraph's Store.

#### Python

```python
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=store
)

# Files persist across different thread_ids
```

#### TypeScript

```typescript
import { createDeepAgent, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store
});
```

### CompositeBackend (Hybrid Storage)

Route different paths to different backends.

#### Python

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),
    routes={
        "/memories/": StoreBackend(rt),  # Persistent storage
    }
)

agent = create_deep_agent(
    backend=composite_backend,
    store=store
)

# /draft.txt -> ephemeral (StateBackend)
# /memories/user-prefs.txt -> persistent (StoreBackend)
```

#### TypeScript

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

## Decision Table: Which Backend to Use

| Use Case | Backend | Why |
|----------|---------|-----|
| Temporary working files | StateBackend | Default, no setup needed |
| Local development CLI | FilesystemBackend | Direct disk access |
| Cross-session memory | StoreBackend | Persists across threads |
| Hybrid storage | CompositeBackend | Mix ephemeral + persistent |
| Production web app | StateBackend or Sandbox | Never use FilesystemBackend |

## Code Examples

### Example 1: Managing Large Context

#### Python

```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Agent offloads search results to filesystem
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Search for information about Python asyncio and save the results for later analysis"
    }]
})

# Agent workflow:
# 1. Use search tool -> large results
# 2. write_file("/search-results.txt", results)
# 3. Continue with compact context
# 4. Later: read_file("/search-results.txt") when needed
```

#### TypeScript

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

### Example 2: Custom Tool Descriptions

#### Python

```python
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        FilesystemMiddleware(
            backend=None,  # Use default StateBackend
            system_prompt="Save intermediate results to /workspace/ directory",
            custom_tool_descriptions={
                "read_file": "Read files you've previously written. Use offset/limit for large files.",
                "write_file": "Save data to avoid context overflow. Organize in /workspace/.",
            }
        ),
    ],
)
```

#### TypeScript

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

### Example 3: Long-term Memory with CompositeBackend

#### Python

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

# Thread 1: Save user preferences
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({
    "messages": [{"role": "user", "content": "Save my preference: I like concise explanations to /memories/prefs.txt"}]
}, config=config1)

# Thread 2: Access saved preferences
config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({
    "messages": [{"role": "user", "content": "Read my preferences and explain asyncio"}]
}, config=config2)
# Agent reads /memories/prefs.txt and provides concise explanation
```

#### TypeScript

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

### Example 4: FilesystemBackend for Local Development (Python)

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(
        root_dir="/Users/username/project",
        virtual_mode=True
    ),
    interrupt_on={"write_file": True, "edit_file": True}  # Safety
)

# Agent can read actual project files
result = agent.invoke({
    "messages": [{"role": "user", "content": "Analyze the code in src/main.py"}]
})
```

## Boundaries

### What Agents CAN Configure

- Backend type and configuration
- Custom tool descriptions
- File paths and organization
- Human-in-the-loop for file operations
- Root directory for FilesystemBackend
- Routing rules for CompositeBackend

### What Agents CANNOT Configure

- Tool names (ls, read_file, write_file, edit_file, glob, grep)
- The fundamental file operation protocol
- Disable filesystem tools in create_deep_agent
- Access files outside virtual_mode restrictions
- Cross-thread file access without proper backend setup

## Gotchas

### 1. StateBackend Files Don't Persist Across Threads

#### Python

```python
# Files lost when thread changes
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Write to /notes.txt"}]}, config=config1)

config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({"messages": [{"role": "user", "content": "Read /notes.txt"}]}, config=config2)
# File not found! Different thread

# Use same thread_id OR use StoreBackend for persistence
```

#### TypeScript

```typescript
// Files lost when thread changes
await agent.invoke({messages: [{role: "user", content: "Write /notes.txt"}]},
  {configurable: {thread_id: "thread-1"}});
await agent.invoke({messages: [{role: "user", content: "Read /notes.txt"}]},
  {configurable: {thread_id: "thread-2"}});
// File not found!

// Use same thread_id OR StoreBackend
```

### 2. FilesystemBackend Needs virtual_mode for Security

#### Python

```python
# Insecure - agent can access anywhere
backend = FilesystemBackend(root_dir="/project", virtual_mode=False)

# Secure - agent restricted to /project
backend = FilesystemBackend(root_dir="/project", virtual_mode=True)
```

#### TypeScript

```typescript
// Insecure
new FilesystemBackend({ rootDir: "/project", virtualMode: false })

// Secure
new FilesystemBackend({ rootDir: "/project", virtualMode: true })
```

### 3. StoreBackend Requires a Store Instance

#### Python

```python
# Missing store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# Provide store
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```

#### TypeScript

```typescript
// Missing store
await createDeepAgent({ backend: (config) => new StoreBackend(config) });

// Provide store
await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```

### 4. edit_file Requires Exact String Match (Python)

```python
# The edit_file tool needs exact string matching

# Won't work - whitespace mismatch
old_string = "def hello():\n  print('hi')"
new_string = "def hello():\n    print('hi')"  # Different indentation

# Match exactly as it appears in the file
old_string = "  print('hi')"  # Exact match from file
new_string = "    print('hi')"  # New content
```

## Links to Documentation

### Python
- [Filesystem Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#filesystem-middleware)
- [Backends Guide](https://docs.langchain.com/oss/python/deepagents/backends)
- [Long-term Memory](https://docs.langchain.com/oss/python/deepagents/long-term-memory)

### TypeScript
- [Filesystem Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#filesystem-middleware)
- [Backends Guide](https://docs.langchain.com/oss/javascript/deepagents/backends)
- [Long-term Memory](https://docs.langchain.com/oss/javascript/deepagents/long-term-memory)
