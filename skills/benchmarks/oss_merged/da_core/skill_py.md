---
name: Deep Agents Core (Python)
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---

<overview>
Deep Agents are an opinionated agent framework built on LangChain/LangGraph with built-in middleware:

- **Task Planning**: TodoListMiddleware for breaking down complex tasks
- **Context Management**: Filesystem tools with pluggable backends
- **Task Delegation**: SubAgent middleware for spawning specialized agents
- **Long-term Memory**: Persistent storage across threads via Store
- **Human-in-the-loop**: Approval workflows for sensitive operations
- **Skills**: On-demand loading of specialized capabilities

The agent harness provides these capabilities automatically - you configure, not implement.
</overview>

<when-to-use>

| Use Deep Agents When | Use LangChain's create_agent When |
|---------------------|-----------------------------------|
| Multi-step tasks requiring planning | Simple, single-purpose tasks |
| Large context requiring file management | Context fits in a single prompt |
| Need for specialized subagents | Single agent is sufficient |
| Persistent memory across sessions | Ephemeral, single-session work |
| CLI or coding assistant use cases | Simple API or chat applications |

</when-to-use>

<ex-basic-agent>
```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",  # Default model
    tools=[get_weather],
    system_prompt="You are a helpful assistant"
)

# Invoke with thread_id for conversation continuity
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Tokyo?"}]
}, config=config)
```
</ex-basic-agent>

<ex-full-configuration>
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    name="my-assistant",
    model="claude-sonnet-4-5-20250929",
    tools=[custom_tool1, custom_tool2],
    system_prompt="Custom instructions",
    middleware=[custom_middleware],
    subagents=[research_agent, code_agent],
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    interrupt_on={"write_file": True},
    skills=["./skills/"],
    checkpointer=MemorySaver(),  # Required for interrupts
    store=InMemoryStore()        # Required for memory
)
```
</ex-full-configuration>

<built-in-tools>
Every deep agent has access to:

1. **Planning**: `write_todos` - Track multi-step tasks
2. **Filesystem**: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
3. **Delegation**: `task` - Spawn specialized subagents
</built-in-tools>

<middleware-selection>

| If you need to... | Use this middleware | Notes |
|------------------|---------------------|-------|
| Track complex tasks | TodoListMiddleware | Default enabled |
| Manage file context | FilesystemMiddleware | Configure backend |
| Delegate work | SubAgentMiddleware | Add custom subagents |
| Add human approval | HumanInTheLoopMiddleware | Requires checkpointer |
| Load skills | SkillsMiddleware | Provide skill directories |
| Access memory | MemoryMiddleware | Requires Store instance |

</middleware-selection>

---

<skill-md-format>
Skills use **progressive disclosure** - agents only load content when relevant.

### Directory Structure
```
skills/
└── my-skill/
    ├── SKILL.md        # Required: main skill file
    ├── examples.py     # Optional: supporting files
    └── templates/      # Optional: templates
```

### SKILL.md Format
```markdown
---
name: my-skill
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---

# Skill Name

## Overview
Brief explanation of the skill's purpose.

## When to Use
Conditions when this skill applies.

## Instructions
Step-by-step guidance for the agent.

## Supporting Files
- examples.py: Usage examples
```
</skill-md-format>

<ex-skills-with-filesystem-backend>
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"],
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Use the langgraph-docs skill to explain state management"
    }]
}, config={"configurable": {"thread_id": "session-1"}})
```
</ex-skills-with-filesystem-backend>

<ex-skills-with-store-backend>
```python
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Load skill content into store
skill_content = """---
name: python-testing
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---
# Python Testing Skill
..."""

store.put(
    namespace=("filesystem",),
    key="/skills/python-testing/SKILL.md",
    value=create_file_data(skill_content)
)

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=store,
    skills=["/skills/"]
)
```
</ex-skills-with-store-backend>

<skills-vs-memory>

| Skills | Memory (AGENTS.md) |
|--------|-------------------|
| On-demand loading | Always loaded at startup |
| Task-specific instructions | General preferences |
| Large documentation | Compact context |
| SKILL.md in directories | Single AGENTS.md file |

</skills-vs-memory>

<boundaries>
### What Agents CAN Configure

- Model selection and parameters
- Additional custom tools
- System prompt customization
- Backend storage strategy
- Which tools require approval
- Custom subagents with specialized tools
- Skill directories and content

### What Agents CANNOT Configure

- Core middleware removal (TodoList, Filesystem, SubAgent always present)
- The write_todos, task, or filesystem tool names
- The fundamental tool-calling loop
- The SKILL.md frontmatter format
</boundaries>

<fix-checkpointer-for-interrupts>
```python
# WRONG: This will error if interrupt_on is set
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# CORRECT: Checkpointer is required for interrupts
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
</fix-checkpointer-for-interrupts>

<fix-store-for-memory>
```python
# WRONG: StoreBackend needs a Store instance
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# CORRECT: Pass a Store instance
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
</fix-store-for-memory>

<fix-backend-for-skills>
```python
# WRONG: Skills won't load without proper backend
agent = create_deep_agent(
    skills=["./skills/"]
)

# CORRECT: Use FilesystemBackend for local skills
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
</fix-backend-for-skills>

<fix-thread-id-for-conversations>
```python
# WRONG: Each invocation is isolated without thread_id
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]})
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]})

# CORRECT: Use consistent thread_id for conversation continuity
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]}, config=config)
```
</fix-thread-id-for-conversations>

<fix-frontmatter-required>
```markdown
# WRONG: Missing frontmatter in SKILL.md
# My Skill
This is my skill...

# CORRECT: Include YAML frontmatter
---
name: my-skill
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---
# My Skill
This is my skill...
```
</fix-frontmatter-required>

<fix-specific-skill-descriptions>
```markdown
# WRONG: Vague description
---
name: helper
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---

# CORRECT: Specific description helps agent decide when to use
---
name: python-testing
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---
```
</fix-specific-skill-descriptions>

<fix-subagent-skills>
```python
# WRONG: Main agent skills NOT inherited by custom subagents
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# CORRECT: Provide skills to subagent explicitly
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Explicit
        ...
    }]
)
```
</fix-subagent-skills>
