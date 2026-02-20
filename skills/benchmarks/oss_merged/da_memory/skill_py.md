---
name: Deep Agents Memory & Filesystem (Python)
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
| Temporary working files | StateBackend | Default, no setup needed |
| Local development CLI | FilesystemBackend | Direct disk access |
| Cross-session memory | StoreBackend | Persists across threads |
| Hybrid storage | CompositeBackend | Mix ephemeral + persistent |
| Production web app | StateBackend or Sandbox | Never use FilesystemBackend |

</backend-selection>

<memory-types>

| Type | Backend | Persistence | Use Case |
|------|---------|------------|----------|
| Short-term | StateBackend | Single thread | Temporary working files |
| Long-term | StoreBackend | Across threads | User preferences, learned patterns |
| Hybrid | CompositeBackend | Mix both | Some persistent, some temporary |

</memory-types>

<ex-default-state-backend>
```python
from deepagents import create_deep_agent

# Default backend (StateBackend) - files only exist within thread
agent = create_deep_agent()

result = agent.invoke({
    "messages": [{"role": "user", "content": "Write notes to /draft.txt"}]
}, config={"configurable": {"thread_id": "thread-1"}})

# /draft.txt is lost when thread ends
```
</ex-default-state-backend>

<ex-composite-backend-for-hybrid>
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

# /draft.txt -> ephemeral (StateBackend)
# /memories/user-prefs.txt -> persistent (StoreBackend)
```
</ex-composite-backend-for-hybrid>

<ex-cross-session-memory>
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
    "messages": [{"role": "user", "content": "Save my coding style preferences to /memories/style.txt: use type hints, async/await"}]
}, config=config1)

# Thread 2: Access preferences (different thread!)
config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({
    "messages": [{"role": "user", "content": "Read my coding preferences and write a function"}]
}, config=config2)
# Agent reads /memories/style.txt and applies preferences
```
</ex-cross-session-memory>

<ex-filesystem-backend-local-dev>
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(
        root_dir=".",  # Root directory
        virtual_mode=True  # IMPORTANT: Restrict path access
    ),
    interrupt_on={"write_file": True, "edit_file": True},  # Safety
    checkpointer=MemorySaver()
)

# Agent can read/write actual files on disk
result = agent.invoke({
    "messages": [{"role": "user", "content": "Read the README.md file"}]
})
```

**Security: Never use FilesystemBackend in web servers - use StateBackend or sandbox instead.**
</ex-filesystem-backend-local-dev>

<ex-store-in-custom-tools>
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
```
</ex-store-in-custom-tools>

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
```python
# WRONG: Missing store instance
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# CORRECT: Provide store
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
</fix-storebackend-requires-store>

<fix-statebackend-files-dont-persist>
```python
# WRONG: Files lost when thread changes
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Write to /notes.txt"}]}, config=config1)

config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({"messages": [{"role": "user", "content": "Read /notes.txt"}]}, config=config2)
# File not found! Different thread

# CORRECT: Use same thread_id OR use StoreBackend/CompositeBackend for persistence
```
</fix-statebackend-files-dont-persist>

<fix-path-prefix-for-persistence>
```python
# With CompositeBackend routing /memories/ to StoreBackend:

# WRONG: Won't be persistent (wrong path)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /prefs.txt"}]
})

# CORRECT: Persistent (matches /memories/ route)
agent.invoke({
    "messages": [{"role": "user", "content": "Save to /memories/prefs.txt"}]
})
```
</fix-path-prefix-for-persistence>

<fix-filesystem-backend-needs-virtual-mode>
```python
# WRONG: Insecure - agent can access anywhere via ../ or ~/
backend = FilesystemBackend(root_dir="/project", virtual_mode=False)

# CORRECT: Secure - agent restricted to /project
backend = FilesystemBackend(root_dir="/project", virtual_mode=True)
```
</fix-filesystem-backend-needs-virtual-mode>

<fix-production-store>
```python
# WRONG: InMemoryStore lost on process restart
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()  # Lost when process ends

# CORRECT: Use PostgresStore for production
from langgraph.store.postgres import PostgresStore
store = PostgresStore(connection_string="postgresql://...")
```
</fix-production-store>

<fix-longest-prefix-match>
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
</fix-longest-prefix-match>
